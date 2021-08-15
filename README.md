# Pulse-couple oscillator simulation

![](sample1.gif)


This application is a real-time (~250 FPS) simulation of [pulse-coupled oscillators](http://www.scholarpedia.org/article/Pulse_coupled_oscillators)

Roughly speaking, a system of pulse-coupled oscillators is a graph (network) of individual oscillators where, when each oscillator reaches its peak state - it 'kicks' its neighbors.

The state of each oscillator in the simulation follows the differential equation
f'(t) = a - b\*f(t), where a and b are user-set parameters. When f(t)=1 for some oscillator, that oscillator's state is reset to zero, and all of its neighbors' states increase by kick\_strength (also user specified).

![](sample2.gif)

![](sample3.gif)

# Features
* Real-time pulse-coupled oscialltor simulation accelerated by CUDA
* User-specified parameters for the simulation
* Intuitive UI built in OpenGL

# Installation and use
1. Install [CUDA](https://docs.nvidia.com/cuda/cuda-installation-guide-linux/index.html)
2. Install [my custom game engine](https://github.com/walley892/engine)
3.
```
git clone https://github.com/walley892/osc
cd osc
// possibly inside of a virtual environment if that's your thing
pip3 install -r requrements.txt
python3 osc-application.py
```
