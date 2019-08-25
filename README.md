# HTM 2D Object Modeling

> See the origin of this project on [this HTM Forum thread](https://discourse.numenta.org/t/2d-object-recognition-project/5465/12?u=rhyolight).

The purpose of this project is to define **2D Object Recognition Tests**.

### Object Schema

Objects exist within a 2D space. The space has a width and height. Each location in the space can be identified with an X and Y integer coordinate. Each location may have a Feature.

Objects can be defined as collections of Features in 2D space. Here is an example object schema containing one feature `X` at 14,5

```yaml
---
name: Some Object
width: 20
height: 20
features:
  - { x: 14, y: 5, data: X }
```

### Features

Features always contain data. A Feature's data is used by the Agent to identify objects.

Initially, all Features consist of a simple data type, but should be extensible to contain any data type. For example, current the current Object Library consists of simple one-character features.

### Object Library

The Object Library can be found in `objects/`. Each YAML file within this directory contains one object definition in the format specified in "Object Schema" above.

There are currently 2 objects in the library.

## Agency

An Agent can exist in a location within an Object space. An Agent observing an object will receive features in space according to the location of its sensors.

![Agent picture](https://discourse-cdn-sjc2.com/standard14/uploads/numenta/original/2X/4/49d9249b29105c9efa9eb0bbfa5b53e7f3ee369a.jpeg)

Each Agent has exactly 4 sensors:
- North (Agent Y - 1)
- South (Agent Y + 1)
- East  (Agent X + 1)
- West  (Agent X - 1)

At one time step, an Agent can be at only one location in Object space. Each sensor has access to the Feature beneath it.

Agents should use their sensors to attempt to identify the object under observation at each time step.

### Test Challenge \#1

### JavaScript
See javascript [readme](javascript/).

Code in the `javascript/` subfolder can be used to visualize Objects in the Object Library.

### Python
See python [readme](python/).

Code in the `python/` subfolder contains the beginnings of simple `Agent` and `Environment` implementations.
