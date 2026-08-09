# LaTeX TikZ Code

- URL: https://chatgpt.com/c/6a6e0034-b2a4-83ea-90c5-eef103df382a
- Created: 2026-08-01T14:18:29.755Z

---

> [image: sediment://file_000000006414822fb5c57daff0f11499]
> Invent a yaml dsl to represent this. Output yaml

```yaml
dsl: process-wiring/v1

workflow:
  id: lemon_meringue_pie
  title: Prepare lemon meringue pie, keeping track of waste

  inputs:
    crust: {type: crust}
    lemon: {type: lemon}
    butter: {type: butter}
    filling_sugar: {type: sugar}
    egg: {type: egg}
    meringue_sugar: {type: sugar}

  steps:
    separate_egg:
      operation: separate
      inputs:
        egg: $inputs.egg
      outputs:
        yolk: egg_yolk
        white: egg_white
        shells: egg_shells

    make_lemon_filling:
      operation: make_lemon_filling
      inputs:
        lemon: $inputs.lemon
        butter: $inputs.butter
        sugar: $inputs.filling_sugar
        yolk: $steps.separate_egg.outputs.yolk
      outputs:
        filling: lemon_filling
        lemon_peel: lemon_peel
        butter_wrapper: butter_wrapper

    fill_crust:
      operation: fill_crust
      inputs:
        crust: $inputs.crust
        filling: $steps.make_lemon_filling.outputs.filling
      outputs:
        pie: unbaked_lemon_pie

    make_meringue:
      operation: make_meringue
      inputs:
        white: $steps.separate_egg.outputs.white
        sugar: $inputs.meringue_sugar
      outputs:
        meringue: meringue

    add_meringue:
      operation: add_meringue
      inputs:
        pie: $steps.fill_crust.outputs.pie
        meringue: $steps.make_meringue.outputs.meringue
      outputs:
        pie: unbaked_pie

  waste:
    - from: $steps.make_lemon_filling.outputs.lemon_peel
      discard_as: organic_waste

    - from: $steps.make_lemon_filling.outputs.butter_wrapper
      discard_as: packaging_waste

    - from: $steps.separate_egg.outputs.shells
      discard_as: organic_waste

  outputs:
    unbaked_pie: $steps.add_meringue.outputs.pie
```

