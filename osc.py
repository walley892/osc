import pycuda.driver as cuda
from pycuda.autoinit import context
from pycuda.compiler import SourceModule
import numpy as np

N_THREADS = 512
N_BLOCKS = 32

class OscController(object):
    def __init__(self, n, m, kick_str = 0.02, dt = 0.001, alpha = 2, beta = 0.1):
        self.states = np.random.rand(n*m).astype(np.float32)
        self.states_gpu = cuda.mem_alloc(self.states.nbytes)
        self.prev_states = cuda.mem_alloc(self.states.nbytes)
        cuda.memcpy_htod(self.states_gpu, self.states)
        cuda.memcpy_dtod(self.prev_states, self.states_gpu, self.states.nbytes)
        self.n = n
        self.m = m
        self.kick_str = kick_str
        self.alpha = alpha
        self.beta = beta
        self.dt = dt
        self.gpu_mod = SourceModule("""
        
        __device__ int2 index_to_coord(int index, int width){
            return {index/width, index%width};
        }
        __device__ int coord_to_index(int2 coord, int width){
            return coord.x*width + coord.y;
        }

            __global__ void advance_states(float* states, int stride, int num, float alpha, float beta, float dt){
                int x = threadIdx.x + blockDim.x*blockIdx.x;
                for(int index = x*stride; index <(x+1)*stride && index < num; ++index){
                    states[index] = states[index] + dt*(alpha - beta*states[index]);
                }
            }
            __global__ void set_to_zero(float* states, float* prevStates, int stride, int num){
                int x = threadIdx.x + blockDim.x*blockIdx.x;
                for(int index = x*stride; index <(x+1)*stride && index < num; ++index){
                    if(prevStates[index] > 1){
                        states[index] = 0;
                    }
                }
            }

            __global__ void get_kicked(float* states, float* prevStates, int stride, int num, int width, int height, float kick_str){
                int x = threadIdx.x + blockDim.x*blockIdx.x;
                for(int index = x*stride; index <(x+1)*stride && index < num; ++index){
                   int2 xy = index_to_coord(index, width);
                   for(int i = max(xy.x-2, 0); i < min(xy.x + 3, height); ++i){
                       for(int j = max(xy.y-2, 0); j < min(xy.y + 3, width); ++j){
                            int id = coord_to_index({i, j}, width);
                            if(prevStates[id] >= 1){
                                states[index] += kick_str;
                            }
                        }
                    }
            }
            }
        """
        )

        self.f_advance = self.gpu_mod.get_function('advance_states')
        self.f_kick = self.gpu_mod.get_function('get_kicked')
        self.f_zero = self.gpu_mod.get_function('set_to_zero')

    def advance_states(self):
        num = self.m*self.n;
        stride = np.int32(max(((num)//(N_THREADS)) + 1, 1))
        self.f_advance(self.states_gpu,
            stride,
            np.int32(self.m*self.n),
            np.float32(self.alpha),
            np.float32(self.beta),
            np.float32(self.dt),
            block=(min(N_THREADS, num),1,1),
        )
        cuda.memcpy_dtod(self.prev_states, self.states_gpu, self.states.nbytes)
        self.f_kick(self.states_gpu,
            self.prev_states,
            stride,
            np.int32(self.m*self.n),
            np.int32(self.n),
            np.int32(self.m),
            np.float32(self.kick_str),
            block=(min(N_THREADS, num),1,1),
        )
        self.f_zero(self.states_gpu,
            self.prev_states,
            stride,
            np.int32(self.m*self.n),
            block=(min(N_THREADS, num),1,1),
        )
        cuda.memcpy_dtoh(self.states, self.states_gpu)
