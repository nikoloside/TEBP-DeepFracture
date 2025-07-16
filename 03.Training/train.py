from Experiments.base import Parser
from Training.base import TrainingProcess
from Utils.utils_wandb import Utils_wandb
from tqdm import tqdm
import time
import datetime
import math

parser = Parser()
opt = parser.getOpt()

print(opt)

training = TrainingProcess(opt)

training.Prepare()

wandb = Utils_wandb(opt)

start_datetime = datetime.datetime.now()
print(f'Train start: {start_datetime.strftime("%Y-%m-%d %H:%M:%S")}')

start_time = time.perf_counter()

for epoch in range(opt.start_epoch, opt.end_epoch, 1):
    actual_samples = min(opt.train_dataset_size, len(training.data_loader.dataset))
    tq = tqdm(total=actual_samples, desc='Epoch {0:04}'.format(epoch))
    
    if epoch == 100:
        training.UpdateLr()
    
    training.Train(tq, wandb, epoch)

    if epoch % opt.sample_interval == 0:
        training.Visualize(epoch)

    if epoch % opt.model_save_interval == 0:
        training.SaveModel(epoch)

    if opt.save_bool:
        training.SaveModel(0)
    
    tq.close()
    print("Finished.")

end_time = time.perf_counter()

print("Train Finished.")
print(f'Train start: {start_datetime.strftime("%Y-%m-%d %H:%M:%S")}')
print(f'Train end: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print('Total cost: {}'.format(datetime.timedelta(seconds=math.ceil(end_time-start_time))))
