# Experiments

## Overview

The `experiments` module contains the necessary components to run our experiments. These components will be used in our pipeline to obtain our raw experimental results.

Here is a simplified overview of how the pipeline works:

```python
for model in models:
    for builder in builders:
        # we evaluate the prompt (builder) and the model

        for data in data_loader:
            message = builder(*(data[column] for column in builder_inputs))
            output = model(message)
            result = validator(output, *(data[column] for column in validator_inputs))

            # save results to a column
            results[model][builder][data] = result
```

Note that the running the experiment and analyzing the results are two separate steps. We will use the output from the pipeline and analyze that using components in the `analysis` module.

## Extending the Experiments

### Models

Models are what we will be evaluating through our experiments. To create a new model:

1. Create a new file under `models/`
2. Extend the `BaseClient` class with the model implementation
3. Add your new model to `models.py`

Then, you can add your model to other experiments by adding it under `models` in the yaml file.

### DataLoader, Builders, and Validators

All of these are closely related to each other and are important for running the experiments. On top of evaluating our models, we will also evaluate the effectiveness of our prompts.

#### DataLoader

The DataLoader is an iterable class which returns a dictionary. It is essentially a class which when iterated gives the column values at every row. To create a new DataLoader:

1. Create a new file under `dataloader/`
2. Extend the `BaseLoader` class with the loader implementation
3. Add your new loader to `loaders.py`

You may also want to add stuff to the `datasets/` folder to use as inputs.

#### Builders

Each builder is a function which takes in a few columns from the DataLoader and returns a prompt to pass to the model. The inputs columns to the builder are the columns specified as the `builder_inputs` in the config yaml. Note that these are passed as args, not kwargs.

To create a new builder:

1. Create a new file under `builders/`
2. Implement your builder function. It can take anything as inputs, but every builder in an experiment should be consistent and take inputs in the exact order specified in `builder_inputs`.
3. Add your new builder to `builders.py`

#### Validator

The validator is responsible for validating the output from the LLM. Like the builder, the input columns to the validator are the columns specified as the `validator_inputs` in the config yaml. Note that these again, are passed as args, not kwargs.

To create a new validator:

1. Create a new file under `validators/`
2. Implement your validator function. Its first input will be the LLM response, and the remaining inputs will be the `validator_inputs` columns. A single validator will be used for the entire experiment.
3. Add your new validator to `validators.py`

Note that the validator can return a metadata object, which will be added as additional columns to the output file of the pipeline. This can be used to track useful information throughout the experiment.
