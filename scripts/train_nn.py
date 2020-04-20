import pandas as pd
import torch, os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extractYear(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y').year

def extractMonth(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y').month

def extractDay(datestr):
    return datetime.strptime(datestr, '%m/%d/%Y').day

fpath = os.path.join(os.path.join(BASE_DIR, "media"), "gv_cleaned.csv")
data = pd.read_csv(fpath)
print(data.head())

data['year'] = list(map(extractYear, data['date']))
data['month'] = list(map(extractMonth, data['date']))
data['day'] = list(map(extractDay, data['date']))

data = data.fillna(0)

data = data[(data.n_killed == 0) & (data.n_injured == 0) & (data.n_guns_involved == 0)].reset_index(drop=True)

print(data.head())
print(data.n_killed.quantile(.99))

qkilled = data.n_killed.quantile(.99)
qinjured = data.n_injured.quantile(.99)

data['prob'] = (data['n_killed'].values + data['n_injured'].values)/(qkilled+qinjured)

def getDataPair(data):
    x = torch.Tensor([data['latitude'].values, data['longitude'].values, data['year'].values, data['month'].values, data['day'].values]).transpose(0,1)
    y = torch.Tensor([data['prob'].values]).transpose(0,1)
    print(x[0], y[0])
    return x, y

train_data = data.iloc[:int(data.shape[0]*0.9), :]
test_data = data.iloc[int(data.shape[0]*0.9):, :]

train_x, train_y = getDataPair(train_data)
test_x, test_y = getDataPair(test_data)

# Use the nn package to define our model and loss function.
model = torch.nn.Sequential(
    torch.nn.Linear(5, 10),
    torch.nn.ReLU(),
    torch.nn.Linear(10, 20),
    torch.nn.ReLU(),
    torch.nn.Conv1d(1, 1, 3, stride=2),
    torch.nn.ReLU(),
    torch.nn.Linear(20, 10),
    torch.nn.ReLU(),
    torch.nn.Linear(10, 1),
    torch.nn.Sigmoid(),
)
loss_fn = torch.nn.MSELoss(reduction='sum')

# Use the optim package to define an Optimizer that will update the weights of
# the model for us. Here we will use Adam; the optim package contains many other
# optimization algoriths. The first argument to the Adam constructor tells the
# optimizer which Tensors it should update.
learning_rate = 1e-6
optimizer = torch.optim.Adadelta(model.parameters())
for epoch in range(500):
    # Forward pass: compute predicted y by passing x to the model.
    y_pred = model(train_x)

    # Compute and print loss.
    loss = loss_fn(y_pred, train_y)
    
    print(epoch, "train", loss.item())

    # Before the backward pass, use the optimizer object to zero all of the
    # gradients for the variables it will update (which are the learnable
    # weights of the model). This is because by default, gradients are
    # accumulated in buffers( i.e, not overwritten) whenever .backward()
    # is called. Checkout docs of torch.autograd.backward for more details.
    optimizer.zero_grad()

    # Backward pass: compute gradient of the loss with respect to model
    # parameters
    loss.backward()

    # Calling the step function on an Optimizer makes an update to its
    # parameters
    optimizer.step()
    torch.save(model, os.path.join(os.path.join(BASE_DIR, "model"), f"model-{epoch}.pth"))

#torch.save(model, os.path.join(os.path.join(BASE_DIR, "model"), f"model-final.pth"))
