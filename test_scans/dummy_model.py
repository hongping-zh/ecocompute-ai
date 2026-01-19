
import torch
import torch.nn as nn

class ExpensiveModel(nn.Module):
    def __init__(self):
        super(ExpensiveModel, self).__init__()
        # Large convolution with no grouping
        self.conv1 = nn.Conv2d(1024, 1024, kernel_size=3, padding=1)
        # Large linear layer
        self.fc = nn.Linear(4096, 4096)
        
    def forward(self, x):
        # Missing residual connection despite being deep-ish logic
        x = self.conv1(x)
        x = nn.ReLU()(x)
        x = self.fc(x)
        return x
