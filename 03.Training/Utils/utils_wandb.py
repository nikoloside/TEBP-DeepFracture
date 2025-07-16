import wandb

class Utils_wandb:
    def __init__(self, opt):
        self.isLogging = opt.log_wandb
        
        if  self.isLogging:
            self.wandb = wandb.init(
                project=opt.projectName,
                name=opt.runName,
                config={
                "learning_rate": opt.lr,
                "architecture": opt.architecture,
                "notes": opt.description,
                "dataset": opt.dataroot,
                "epochs": opt.end_epoch,
                }
            )

    def log(self, data):
        if  self.isLogging:
            self.wandb.log(data)
        return