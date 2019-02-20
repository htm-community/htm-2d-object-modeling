# HTM 2D Object Modeling

See the origin of this project on [this HTM Forum thread](https://discourse.numenta.org/t/2d-object-recognition-project/5465/12?u=rhyolight). 

Because we are restricting this project to a 2D space, we don't have to think about _orientation_. 

### Object Space

The experiment space is a simple 2D grid. At each position on the grid has a feature. I'm representing different features below with a black :black_circle: , blue :heavy_multiplication_x:, and green :heavy_check_mark: 

![2d-smi-grid|553x499](https://discourse-cdn-sjc2.com/standard14/uploads/numenta/original/2X/3/3ff95fe491a08da792963c810abed83d7873d122.jpeg) 

The features above are arbitrary. **You can think about this space as an _object_ and the positions as locations on the object, each having a feature.** 

### Agent & Sensors

There is an agent that moves through this object space with sensors. In the example above, the agent is at X10 Y9:

![2d-smi-agent|690x218](https://discourse-cdn-sjc2.com/standard14/uploads/numenta/original/2X/4/49d9249b29105c9efa9eb0bbfa5b53e7f3ee369a.jpeg) 

### Movement

We should restrict movement (initially) so our agent can only move on unit either :arrow_up::arrow_down::arrow_left::arrow_right: (no diagonal). I also want to initially use random movements (we'll talk about control when we need to).

With this setup, for any movement, we'll get 4 new sensory inputs (one for each sensor at NSEW). As the agent moves, sensors build up their models of the object. 

### Cortical Columns

Here's the hard part. We need to build a **3-layer Network** _for each sensor_ which has an object pooling layer as described in the [Columns Paper](https://numenta.com/neuroscience-research/research-publications/papers/a-theory-of-how-columns-in-the-neocortex-enable-learning-the-structure-of-the-world/) above a 2-layer location/sensor circuit as described in [ Columns+](https://numenta.com/neuroscience-research/research-publications/papers/locations-in-the-neocortex-a-theory-of-sensorimotor-object-recognition-using-cortical-grid-cells/):

![IMG_0028E2B3C1FD-1|391x500](https://discourse-cdn-sjc2.com/standard14/uploads/numenta/original/2X/5/5a2774f685211b897eaba81aedfb9c53dc564e83.jpeg) 

Linked together with lateral connectivity:

![IMG_900C54CC0FF5-1|690x269](https://discourse-cdn-sjc2.com/standard14/uploads/numenta/original/2X/b/ba8f4d557d4973aa5824ac2681dacad7c3481aef.jpeg) 
