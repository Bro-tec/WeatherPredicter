import CollectData.get_learning_data as gld
import matplotlib.pyplot as plt
import os
import json
from datetime import datetime as dt
from datetime import timedelta as td
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle

# from sklearn import preprocessing as pr
from sklearn.model_selection import train_test_split

# from sklearn.metrics import accuracy_score
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
from torchmetrics.classification import MulticlassConfusionMatrix
import math
import warnings
import random

plt.switch_backend("agg")

warnings.filterwarnings("ignore")


# checking if cuda is used. if not it choses cpu
def check_cuda():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print("this device uses " + device + " to train data")
    return torch.device(device)


# creating my lstm
class PyTorch_LSTM(nn.Module):
    def __init__(
        self,
        inputs,
        outputs,
        device,
        h_size=30,
        seq_size=24,
        batchsize=100,
        layer=3,
        dropout=0,
    ):
        super(PyTorch_LSTM, self).__init__()
        self.lstm = nn.LSTM(
            input_size=inputs,
            hidden_size=h_size,
            num_layers=layer,
            dropout=dropout,
            batch_first=True,
        ).to(device)
        # self.fc2 = nn.Linear(seq_size, 1).to(device)
        self.fc = nn.Linear(h_size, outputs).to(device)
        self.hidden_state = Variable(
            torch.Tensor(np.zeros((layer, batchsize, h_size)).tolist())
            .type(torch.float32)
            .to(device)
        ).to(device)
        self.cell_state = Variable(
            torch.Tensor(np.zeros((layer, batchsize, h_size)).tolist())
            .type(torch.float32)
            .to(device)
        ).to(device)

    def show_hiddens(self):
        print(
            "hidden_state:\n",
            self.hidden_state.tolist(),
            "\ncell_state:\n",
            self.cell_state.tolist(),
        )

    def set_hiddens(self, batchsize, device):
        self.hidden_state = Variable(
            torch.Tensor(
                np.zeros(
                    (self.hidden_state.shape[0], batchsize, self.hidden_state.shape[-1])
                ).tolist()
            )
            .type(torch.float32)
            .to(device)
        ).to(device)
        self.cell_state = Variable(
            torch.Tensor(
                np.zeros(
                    (self.cell_state.shape[0], batchsize, self.cell_state.shape[-1])
                ).tolist()
            )
            .type(torch.float32)
            .to(device)
        ).to(device)

    def forward(self, input, device, hiddens=True):
        out, (hn, cn) = self.lstm(input, (self.hidden_state, self.cell_state))
        if hiddens:
            self.hidden_state = hn.detach()
            self.cell_state = cn.detach()
        # print("out", out.shape)
        l = self.fc(out[:, -1, :])
        # print("l2", l2.shape)

        return l.type(torch.float64).to(device)


# loading model if already saved or creating a new model
def load_own_Model(
    name,
    device,
    input_count=230,
    output_count=46,
    learning_rate=0.001,
    layer=3,
    hiddensize=7,
    sequences=24,
    dropout=0.1,
    batchsize=0,
):
    history = {
        "accuracy": [0],
        "loss": [0],
        "val_accuracy": [0],
        "val_loss": [0],
        # "argmax_accuracy": [0],
        # "val_argmax_accuracy": [0],
    }
    model = {"haha": [1, 2, 3]}

    if os.path.exists(f"./Models/{name}.pth"):
        checkpoint = torch.load(f"./Models/{name}.pth", map_location=device)
        model = checkpoint["model"]
    else:
        print("Data not found or not complete")
        model = PyTorch_LSTM(
            input_count,
            output_count,
            device,
            h_size=hiddensize,
            seq_size=sequences,
            layer=layer,
            dropout=dropout,
            batchsize=batchsize,
        )
    if os.path.exists(f"./Models/{name}_history.json"):
        with open(f"./Models/{name}_history.json", "r") as f:
            history = json.load(f)
        print("Model found")
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    if os.path.exists(f"./Models/{name}.pth"):
        checkpoint = torch.load(f"./Models/{name}.pth", map_location=device)
        optimizer.load_state_dict(checkpoint["optimizer"])
    model.train()
    # metric = MulticlassConfusionMatrix(num_classes=21).to(device)
    return model, optimizer, history


# saving model if saving_mode set to ts or timestamp it will use the number for the model to save it.
# ts helps to choose saved model data before the model started to overfit or not work anymore
def save_own_Model(name, history, model, optimizer):
    with open(f"./Models/{name}_history.json", "w") as fp:
        json.dump(history, fp)
    torch.save(
        {"model": model, "optimizer": optimizer.state_dict()},
        f"./Models/{name}.pth",
    )
    print("Saved model")


def approximation(all):
    x = np.arange(0, len(all))
    y = list(all)
    [b, m] = np.polynomial.polynomial.polyfit(x, y, 1)
    # print("b: ", b, ", m: ", m)
    return b, m


# plotting Evaluation via Accuracy, Loss and MulticlassConfusionMatrix
def plotting_hist(history, metrics, name, min_amount=2, epoche=0):
    icons = [
        None,
        "clear-day",
        "clear-night",
        "partly-cloudy-day",
        "partly-cloudy-night",
        "cloudy",
        "fog",
        "wind",
        "rain",
        "sleet",
        "snow",
        "hail",
        "thunderstorm",
        "dry",
        "moist",
        "wet",
        "rime",
        "ice",
        "glaze",
        "not dry",
        "reserved",
    ]
    directions = [
        "up",
        "right_up",
        "right",
        "right_down",
        "down",
        "down_left",
        "left",
        "left_up",
        "None",
    ]
    name_tag = f"{name}_plot"
    # summarize history for accuracy
    fig, ax = plt.subplots(4, figsize=(20, 5), sharey="row")
    plt.title("model accuracy")
    plt.ylabel("accuracy")
    plt.xlabel("epoch")
    plt.title("model accuracy")
    ax[0].plot(history["accuracy"][1:])
    ax[0].plot(history["val_accuracy"][1:])
    if len(history["accuracy"]) > 150:
        ax[1].plot(history["accuracy"][-150:], alpha=0.6)
        ax[1].plot(history["val_accuracy"][-150:], alpha=0.6)
    if len(history["accuracy"]) > min_amount:
        ax[2].plot(history["accuracy"][(-1 * min_amount) :])
        ax[3].plot(history["val_accuracy"][(-1 * min_amount) :])
    ax[0].grid(axis="y")
    ax[1].grid(axis="y")
    ax[2].grid(axis="y")
    ax[3].grid(axis="y")
    ax[0].legend(
        [
            "train",
            "test",
        ],
        # ["svm train", "svm test", "rf train", "rf test"],
        loc="upper left",
    )
    ax[1].legend(
        [
            "train",
            "test",
        ],
        loc="upper left",
    )
    plt.legend(["train", "test"], loc="upper left")
    plt.savefig(f"./Plots/{name_tag}_accuracy.png")
    plt.close()

    # summarize history for loss
    plt.title("model loss")
    plt.ylabel("loss")
    plt.xlabel("epoch")

    history["loss"] = (pd.Series(history["loss"])).tolist()
    history["val_loss"] = (pd.Series(history["val_loss"])).tolist()
    history["loss"] = [-_ if _ < 0 else _ for _ in history["loss"]]
    history["val_loss"] = [-_ if _ < 0 else _ for _ in history["val_loss"]]

    b, m = approximation(history["loss"])
    f = [b + (m * x) for x in range(len(history["loss"]))]
    b2, m2 = approximation(history["loss"][-150:])
    f2 = [b2 + (m2 * x) for x in range(150)]
    # summarize history for loss
    fig, ax = plt.subplots(4, figsize=(20, 5), sharey="row")

    ax[0].plot(history["loss"], alpha=0.8)
    ax[0].plot(history["val_loss"], alpha=0.75)
    ax[0].plot(f)
    ax[0].grid(axis="y")
    ax[0].legend(
        [
            "train / Epoche:" + str(epoche + 1),
            "test",
            # "linear train: {:.1f} + {:.5f}x".format(b * 10, m),
            "linear train: {:.5f}x".format(m),
        ],
        loc="upper left",
    )
    ax[1].plot(history["loss"][-150:], alpha=0.8)
    ax[1].plot(history["val_loss"][-150:], alpha=0.75)
    ax[1].plot(f2)
    ax[1].grid(axis="y")
    ax[1].legend(
        [
            "train",
            "test",
            # "linear train: {:.1f} + {:.5f}x".format(b2 * 10, m2),
            "linear train: {:.5f}x".format(m2),
        ],
        loc="upper left",
    )
    ax[2].plot(history["loss"][(-1 * min_amount) :])
    ax[2].grid(axis="y")
    ax[3].plot(history["val_loss"][(-1 * min_amount) :])
    ax[3].grid(axis="y")
    plt.savefig(f"./Plots/{name_tag}_loss.png")
    plt.close()

    # summarize MulticlassConfusionMatrix
    fig, ax = plt.subplots(
        3,
        2,
        figsize=(8, 16),
        sharey="row",
    )
    plt.title("Confusion Matrix")
    metric_names = [
        "Train direction",
        "Test Icon",
        "Train Icon",
        "Test Icon",
        "Train Condition",
        "Test Condition",
    ]
    ax[0, 0].title.set_text(metric_names[0])
    metrics[0].plot(
        ax=ax[0, 0],
        # cmap="Blues",
        # colorbar=False,
    )
    ax[0, 0].xaxis.set_ticklabels(directions)
    ax[0, 0].yaxis.set_ticklabels(directions)
    ax[0, 1].title.set_text(metric_names[1])
    metrics[1].plot(
        ax=ax[0, 1],
        # cmap="Blues",
        # colorbar=False,
    )
    ax[0, 1].xaxis.set_ticklabels(directions)
    ax[0, 1].yaxis.set_ticklabels(directions)
    for i in range(2, len(metrics)):
        j = math.floor(i / 2)
        k = i % 2
        ax[j, k].title.set_text(metric_names[i])
        metrics[i].plot(
            ax=ax[j, k],
            # cmap="Blues",
            # colorbar=False,
        )
        ax[j, k].xaxis.set_ticklabels(icons)
        ax[j, k].yaxis.set_ticklabels(icons)
    fig.set_figwidth(20)
    fig.set_figheight(20)
    plt.savefig(f"./Plots/{name_tag}_matrix.png")
    plt.close()


# unscaling the output because it usually doesnt get over 1
def unscale_output(output):
    output[:, 0] *= 100
    output[:, 1] *= 100
    output[:, 2] *= 10000
    return output


# scaling label to check if output was good enough
def scale_label(output):
    output[:, 0] /= 100
    output[:, 1] /= 100
    output[:, 2] /= 10000
    # output[:, :, 4] /= 21
    # output[:, :, 5] /= 21
    return output


def scale_features(output):
    for i in range(5):
        output[:, :, i * 5] /= 100
        output[:, :, 1 + i * 5] /= 100
        output[:, :, 2 + i * 5] /= 10000
        # output[:, :, 4 + i * 5] /= 21
        # output[:, :, 5 + i * 5] /= 21
    return output


def clean_torch(val):
    val[val != val] = 0.0
    return val


# whole training of the LSTM features and labels need to be 2d shaped
def train_LSTM(
    name,
    feature,
    label,
    model,
    optimizer,
    history,
    device,
    epoch_count=1,
    epoch=0,
    batchsize=0,
):
    MSEloss_fn = nn.MSELoss().to(device)
    CE1loss_fn = nn.CrossEntropyLoss().to(device)
    CE2loss_fn = nn.CrossEntropyLoss().to(device)
    CE3loss_fn = nn.CrossEntropyLoss().to(device)
    if batchsize == 0:
        batchsize == len(feature)

    X_train, X_test, y_train, y_test = train_test_split(
        feature, label, test_size=0.02, random_state=42
    )
    X_train_tensors = Variable(torch.Tensor(X_train).to(device)).to(device)
    X_test_tensors = Variable(torch.Tensor(X_test).to(device)).to(device)
    y_train_tensors = Variable(torch.Tensor(y_train)).to(device)
    y_test_tensors = Variable(torch.Tensor(y_test)).to(device)

    # print("X_train_tensors", X_train_tensors.shape)
    # print("y_train_tensors", y_train_tensors.shape)
    # print("X_test_tensors", X_test_tensors.shape)
    # print("y_test_tensors", y_test_tensors.shape)

    X_train_tensors = scale_features(X_train_tensors)
    y_train_tensors = scale_label(y_train_tensors)
    X_test_tensors = scale_features(X_test_tensors)
    y_test_tensors = scale_label(y_test_tensors)
    metrics = [
        MulticlassConfusionMatrix(num_classes=9).to(device) for i in range(2)
    ] + [MulticlassConfusionMatrix(num_classes=21).to(device) for i in range(4)]

    acc_list = []
    loss_list = []
    labels = Variable(torch.Tensor(np.array(y_train.tolist())).to(device)).to(
        device
    )  # .flatten()
    val_labels = Variable(torch.Tensor(np.array(y_test.tolist())).to(device)).to(
        device
    )  # .flatten()
    val_loss_list = []
    val_acc_list = []

    # trains the value using each input and label
    for batches in tqdm(range(math.ceil(X_train_tensors.shape[0] / batchsize))):
        model.train()
        output = 0
        scaled_batch = 0
        # print("batches", batches)

        if batches >= math.ceil(X_train_tensors.shape[0] / batchsize) - 1:
            model.set_hiddens(X_train_tensors[batches * batchsize :].shape[0], device)
            # print("runs")
            output = model.forward(
                X_train_tensors[batches * batchsize :], device, hiddens=False
            )
            scaled_batch = y_train_tensors[batches * batchsize :].detach().clone()
            train_label = labels[batches * batchsize :]
        else:
            model.set_hiddens(batchsize, device)
            output = model.forward(
                X_train_tensors[batches * batchsize : (batches + 1) * batchsize],
                device,
                hiddens=False,
            )
            scaled_batch = (
                y_train_tensors[batches * batchsize : (batches + 1) * batchsize]
                .detach()
                .clone()
            )
            train_label = labels[batches * batchsize : (batches + 1) * batchsize]

        torch_outputs = output.detach().clone()
        # print("output", output.shape, "\nscaled_batch", scaled_batch.shape)
        loss = MSEloss_fn(output[:, :3], scaled_batch[:, :3].double())
        loss += CE1loss_fn(output[:, 3:12], torch.max(scaled_batch[:, 3:12], dim=1)[1])
        loss += CE2loss_fn(
            output[:, 12:33], torch.max(scaled_batch[:, 12:33], dim=1)[1]
        )
        loss += CE3loss_fn(
            output[:, 33:54], torch.max(scaled_batch[:, 33:54], dim=1)[1]
        )
        # calculates the loss of the loss function
        loss.backward()
        # improve from loss, this is the actual backpropergation
        optimizer.step()
        # caluclate the gradient, manually setting to 0
        optimizer.zero_grad()

        loss_list.append(float(loss.item()))

        size = torch_outputs.shape[0]

        compare = torch_outputs[:, :4] - scaled_batch[:, :4]
        compare[compare < 0] *= -1
        acc_list.append(100 / (1 + ((compare).float().sum() / (size * 4))))
        _, inds_o_direction = torch.max(torch_outputs[:, 3:12], dim=1)
        _, inds_s_direction = torch.max(scaled_batch[:, 3:12], dim=1)
        _, inds_o_icon = torch.max(torch_outputs[:, 12:33], dim=1)
        _, inds_s_icon = torch.max(scaled_batch[:, 12:33], dim=1)
        _, inds_o_condition = torch.max(torch_outputs[:, 33:54], dim=1)
        _, inds_s_condition = torch.max(scaled_batch[:, 33:54], dim=1)
        acc_list.append(
            (inds_o_direction == inds_s_direction).sum().item() / size * 100
        )
        acc_list.append((inds_o_icon == inds_s_icon).sum().item() / size * 100)
        acc_list.append(
            (inds_o_condition == inds_s_condition).sum().item() / size * 100
        )

        metrics[0].update(
            torch.argmax(torch_outputs[:, 3:12], dim=1),
            torch.argmax(scaled_batch[:, 3:12], dim=1),
        )
        metrics[2].update(
            torch.argmax(torch_outputs[:, 12:33], dim=1),
            torch.argmax(scaled_batch[:, 12:33], dim=1),
        )
        metrics[3].update(
            torch.argmax(torch_outputs[:, 33:54], dim=1),
            torch.argmax(scaled_batch[:, 33:54], dim=1),
        )

    my_acc = torch.FloatTensor(acc_list).to(device)
    my_acc = clean_torch(my_acc).mean()
    my_loss = torch.FloatTensor(loss_list).to(device)
    my_loss = clean_torch(my_loss).mean()

    # showing training
    if my_loss != "NaN":
        history["loss"].append(float(my_loss) / 100)
    else:
        history["loss"].append(history["loss"][-1])

    if my_acc != "NaN":
        history["accuracy"].append(float(my_acc))
    else:
        history["accuracy"].append(history["accuracy"][-1])
    print(
        "\nEpoch {}/{}, Loss: {:.5f}, Accuracy: {:.5f} \n".format(
            epoch + 1, epoch_count, my_loss, my_acc
        )
    )

    # testing trained model on unused values
    model.eval()
    for batches in tqdm(range(math.ceil(X_test_tensors.shape[0] / batchsize))):
        output = 0
        scaled_batch = 0
        with torch.no_grad():
            if batches >= math.ceil(X_test_tensors.shape[0] / batchsize) - 1:
                model.set_hiddens(
                    X_test_tensors[batches * batchsize :].shape[0], device
                )
                # print("runs")
                output = model.forward(
                    X_test_tensors[batches * batchsize :], device, hiddens=False
                )
                scaled_batch = y_test_tensors[batches * batchsize :]
                test_label = val_labels[batches * batchsize :]
            else:
                model.set_hiddens(batchsize, device)
                output = model.forward(
                    X_test_tensors[batches * batchsize : (batches + 1) * batchsize],
                    device,
                    hiddens=False,
                )
                scaled_batch = y_test_tensors[
                    batches * batchsize : (batches + 1) * batchsize
                ]
                test_label = val_labels[batches * batchsize : (batches + 1) * batchsize]

            val_torch_outputs = output.detach().clone()
            # del output, input

            # loss
            val_loss = MSEloss_fn(output[:, :3], scaled_batch[:, :3].double())
            val_loss += CE1loss_fn(
                output[:, 3:12], torch.max(scaled_batch[:, 3:12], dim=1)[1]
            )
            val_loss += CE2loss_fn(
                output[:, 12:33], torch.max(scaled_batch[:, 12:33], dim=1)[1]
            )
            val_loss += CE3loss_fn(
                output[:, 33:54], torch.max(scaled_batch[:, 33:54], dim=1)[1]
            )
            val_loss_list.append(float(val_loss.item()))

        size = val_torch_outputs.shape[0]
        compare = val_torch_outputs[:, :4] - scaled_batch[:, :4]
        # compare = val_torch_outputs[1:] - scaled_val_label
        compare[compare < 0] *= -1
        val_acc_list.append(100 / (1 + ((compare).float().sum() / (size * 4))))
        _, inds_o_direction = torch.max(val_torch_outputs[:, 3:12], dim=1)
        _, inds_s_direction = torch.max(scaled_batch[:, 3:12], dim=1)
        _, inds_o_icon = torch.max(val_torch_outputs[:, 12:33], dim=1)
        _, inds_s_icon = torch.max(scaled_batch[:, 12:33], dim=1)
        _, inds_o_condition = torch.max(val_torch_outputs[:, 33:54], dim=1)
        _, inds_s_condition = torch.max(scaled_batch[:, 33:54], dim=1)
        val_acc_list.append(
            (inds_o_direction == inds_s_direction).sum().item() / size * 100
        )
        val_acc_list.append((inds_o_icon == inds_s_icon).sum().item() / size * 100)
        val_acc_list.append(
            (inds_o_condition == inds_s_condition).sum().item() / size * 100
        )
        # print(val_acc_list[-3:])
        # metric_output = unscale_output(output)
        # print("metric", metric_output[:, 4:25].shape, test_label[:, 4:25].shape)
        # print("metric", metric_output[:, -21:].shape, test_label[:, -21:].shape)
        metrics[1].update(
            torch.argmax(output[:, 3:12], dim=1),
            torch.argmax(scaled_batch[:, 3:12], dim=1),
        )
        metrics[4].update(
            torch.argmax(output[:, 12:33], dim=1),
            torch.argmax(scaled_batch[:, 12:33], dim=1),
        )
        metrics[5].update(
            torch.argmax(output[:, 33:54], dim=1),
            torch.argmax(scaled_batch[:, 33:54], dim=1),
        )

    my_val_acc = torch.FloatTensor(val_acc_list).to(device)
    # setting nan values to 0 to calculate the mean
    my_val_acc = clean_torch(my_val_acc).mean()
    my_val_loss = torch.FloatTensor(val_loss_list).to(device)
    my_val_loss = clean_torch(my_val_loss).mean()

    if my_val_loss != "NaN":
        # history["val_loss"].append(convert_loss(float(my_val_loss)))
        history["val_loss"].append(float(my_val_loss) / 100)
    else:
        history["val_loss"].append(history["val_loss"][-1])

    if my_val_acc != "NaN":
        # history["val_accuracy"].append(convert_loss(float(my_val_acc)))
        history["val_accuracy"].append(float(my_val_acc))
    else:
        history["val_accuracy"].append(history["val_accuracy"][-1])
    print(
        "\nEpoch {}/{}, val Loss: {:.8f}, val Accuracy: {:.5f}".format(
            # epoch + 1, epoch_count, convert_loss(my_val_loss), my_val_acc
            epoch + 1,
            epoch_count,
            my_val_loss,
            my_val_acc,
        )
    )

    return model, history, metrics, optimizer


# plotting predicted data only for hourly named models
# future predictions has no labels so they can't be printed
def plotting_Prediction_hourly(
    all_input, output, plot_text, hourly=[], hourly24=[], mode="normal", t=0
):
    titles = ["Temperature", "Wind direction", "Wind speed", "Visibility"]
    input = [
        all_input[3],
        all_input[4],
        all_input[5],
        all_input[9],
        all_input[12],
        all_input[16],
    ]
    x = [1, 2, 25]
    name = "Hourly"
    fig, axs = plt.subplots(len(titles) + 1, 1, figsize=(12, 8))
    for i in range(len(titles)):
        axs[i].set_title(titles[i])
        axs[i].plot(x, [input[i], output[0][0][i].item(), output[1][0][i].item()])
        if plot_text != "future":
            axs[i].plot(x, [input[i], hourly[i], hourly24[i]])
        axs[len(titles)].text(
            0,
            0.3,
            f"icon: real-{hourly[4]} / prediction-{output[0][0][4]}, condition: real-{hourly[4]}/ prediction-{output[0][0][5]}",
            fontsize=15,
        )
        axs[len(titles)].text(
            0,
            0.6,
            f"24 icon: real-{hourly24[4]} / prediction-{output[1][0][4]}, condition: real-{hourly24[4]}/ prediction-{output[1][0][5]}",
            fontsize=15,
        )

    if plot_text != "future":
        axs[0].legend(["predicted", "real"], loc="upper left")
    fig.suptitle(f"prediction {plot_text}")
    plt.tight_layout()
    if mode == "timestep" or mode == "ts":
        plt.savefig(f"./Plots/{name}_{t}_prediction_{plot_text}.png")
    else:
        plt.savefig(f"./Plots/{name}_prediction_{plot_text}.png")


# aktively used reshaping and predicting
def prediction(model, train, name, device):
    train_tensors = Variable(torch.Tensor(train).to(device)).to(device)
    input_final = torch.reshape(train_tensors, (1, 1, train_tensors.shape[-1])).to(
        device
    )
    output = model.forward(input_final, device)
    output = unscale_output(output=output, name=name)
    return [output]


# prediction main code specially for hourly models
def predictHourly(date, device, mode="normal", model_num=0, id="", city="", time=-1):
    out_list = []
    if date <= dt.now() - td(days=2):
        train, label, label24 = gld.get_predictDataHourly(date, id=id)
        if isinstance(train, str):
            print("error occured please retry with other ID/Name")
            return
        print("\ntraining count", train.shape)

        model, optimizer, loss_fn, metric, history = load_own_Model(
            "Hourly", device, loading_mode=mode, t=model_num
        )
        model24, optimizer24, loss_fn24, metric24, history24 = load_own_Model(
            "Hourly24", device, loading_mode=mode, t=model_num
        )
        if not id == "" or city == "":
            out_list.append(prediction(model, train[time], "Hourly", device))
            out_list.append(prediction(model24, train[time], "Hourly", device))
            plotting_Prediction_hourly(
                train[time],
                out_list,
                "test",
                hourly=label[time],
                hourly24=label24[time],
                mode=mode,
                t=model_num,
            )
    else:
        train = gld.get_predictDataHourly(date, id=id)
        if isinstance(train, str):
            print("error occured please retry with other ID/Name")
            return
        print("\ntraining count", train.shape)
        model, optimizer, loss_fn, metric, history = load_own_Model(
            "Hourly", device, loading_mode=mode, t=model_num
        )
        model24, optimizer24, loss_fn24, metric24, history24 = load_own_Model(
            "Hourly24", device, loading_mode=mode, t=model_num
        )
        if not id == "" or city == "":
            out_list.append(prediction(model, train[time], "Hourly", device))
            out_list.append(prediction(model24, train[time], "Hourly", device))
            plotting_Prediction_hourly(
                train[time], out_list, "future", mode=mode, t=model_num
            )
