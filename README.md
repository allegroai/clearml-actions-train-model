# GitHub Action For Running Experiments With ClearML

![GitHub stars](https://img.shields.io/github/stars/allegroai/clearml?style=social)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/allegroai/clearml-actions-train-model/Test%20train%20model)


Train models easily with ClearML, directly from your repo!
 
This action helps to run experiments with , directly from Github. 
Just comment from any issue or pull request with 
  - `/train-model branch <brach name>`
  - `/train-model tag <tag_name> `
  - `/train-model commit <commit_id>`


## Usage
### Workflow Example
This will add an action to your workflow that will clone a ClearML [Task](https://clear.ml/docs/latest/docs/fundamentals/task)
 `TASK_ID` and will enqueue it to selected [Queue](https://clear.ml/docs/latest/docs/fundamentals/agents_and_queues) (`QUEUE_NAME` input parameter). 

Works both in github issues and github pull requests comments.
![image](docs/clearml-train-model-flow.png)



```yaml
name: Train model
on: [issue_comment]

jobs:
  train-model:
      if: contains(github.event.comment.body, '/train-model')
      runs-on: ubuntu-latest
      steps:
        - name: Train model
          uses: allegroai/clearml-train-model@master
          id: train
          with:
            CLEARML_API_ACCESS_KEY: ${{ secrets.ACCESS_KEY }}
            CLEARML_API_SECRET_KEY: ${{ secrets.SECRET_KEY }}
            CLEARML_API_HOST: ${{ secrets.CLEARML_API_HOST }}
            TASK_ID: "e4623efdfa1d461e9101615728fdc52e"
            QUEUE_NAME: "train_queue"
          env:
            GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        # Example how you can use outputs from the train action
        - name: Print task status
          run: |
            echo "Task stats is ${TASK_STATUS} for task ${CLONED_TASK}"
          env:
            TASK_STATUS: ${{ steps.train.outputs.TASK_STATUS }}
            CLONED_TASK: ${{ steps.train.outputs.CLONED_TASK }}
```

### Inputs

#### Mandatory
  1. `CLEARML_API_ACCESS_KEY`: Your ClearML api access key. You can find it in your clearml.conf file under api.credentials.access_key section, [read more](https://clear.ml/docs/latest/docs/). 
  2. `CLEARML_API_SECRET_KEY`: Your ClearML api secret key. You can find it in your clearml.conf file under api.credentials.secret_key section, [read more](https://clear.ml/docs/latest/docs/).
  3. `CLEARML_API_HOST`: The ClearML api server address. You can find it in your clearml.conf file under  api.api_server section, [read more](https://clear.ml/docs/latest/docs/).
  4. `TASK_ID`: Id of the task you would like to clone.

#### Optional

  1. `QUEUE_NAME`: Queue for the cloned task (default value: `default`). You can read more about queues [here](https://clear.ml/docs/latest/docs/getting_started/mlops/mlops_first_steps).
  
### Outputs

1. `CLONED_TASK`: The cloned task id.
2. `TASK_STATUS`: The cloned task status (not updating).
