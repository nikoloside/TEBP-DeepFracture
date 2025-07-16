import os
import nibabel as nib
from Utils.animator3d import MedicalImageAnimator
from Utils.utils_device import get_device, to_device
import torch
import numpy as np

import torch.nn.init as init
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import axes3d
from io import BytesIO
from PIL import Image

class Utils_visualize:
    # Nibabel Saving
    @staticmethod
    def save_as_nib(file_name, variable):
        ni_img = nib.Nifti1Image(variable, affine=np.eye(4))
        nib.save(ni_img, file_name)

    # Step save 
    @staticmethod
    def drawPredict(encoder, model, pos, direct, imp, x_middle, x_big, ind, epoch, save_path, opt):
        if epoch == 0:
            gif_path = os.path.join(save_path, 'truth_%d.gif' % (ind))
            animator = MedicalImageAnimator(x_middle.to('cpu').detach().numpy().copy().squeeze(), [], 0, save=True)
            animate = animator.run(gif_path)

            x_md_region = x_middle.clone().detach()
            x_md_region[x_md_region < 0] = 0
            gif_path = os.path.join(save_path, 'truth_%d_region.gif' % (ind))
            animator = MedicalImageAnimator(x_md_region.to('cpu').detach().numpy().copy().squeeze(), [], 0, save=True)
            animate = animator.run(gif_path)

            x_md_mask = x_middle.clone().detach()
            x_md_mask[x_md_mask >= 0] = 1
            x_md_mask[x_md_mask < 0] = 0
            gif_path = os.path.join(save_path, 'truth_%d_mask.gif' % (ind))
            animator = MedicalImageAnimator(x_md_mask.to('cpu').detach().numpy().copy().squeeze(), [], 0, save=True)
            animate = animator.run(gif_path)

            # vox_path = os.path.join(save_path, 'truth_%d.nii' % (ind))
            # Utils_visualize.save_as_nib(vox_path, x_middle.to('cpu').detach().numpy().copy())

            f_input_path = os.path.join(save_path, 'truth_%d.txt' % (ind))
            f_input = open(f_input_path, "w")
            f_input.write('{ pos: [%f, %f, %f], direct: [%f, %f, %f], imp: %f }' % (pos[0,0].item(), pos[0,1].item(), pos[0,2].item(), direct[0, 0].item(), direct[0, 1].item(), direct[0, 2].item(), imp.item()))
            f_input.close()

        # 获取设备
        device = get_device(getattr(opt, 'use_cuda', True))
        
        feature = encoder.predict(pos, direct, imp)
        if ind.item() < opt.train_dataset_size:
            latent_z = model.codes()[ind]
        else:
            latent_z = torch.FloatTensor(1, opt.z_latent_dim, device=device)
            init.xavier_normal_(latent_z)

        input_x, min_index, dist = model.Cook(feature, latent_z)

        # Middle
        output = model.forwardMiddle(input_x).squeeze().squeeze()

        x_md_region = output.clone().detach()
        x_md_region[x_md_region < 0] = 0

        x_md_mask = output.clone().detach()
        x_md_mask[x_md_mask >= 0] = 1
        x_md_mask[x_md_mask < 0] = 0

        gif_path = os.path.join(save_path, 'test_epoch_%d_ind_%d-vq-poc-%d-md.gif' % (epoch, ind, min_index))
        animator = MedicalImageAnimator(output.to('cpu').detach().numpy().copy(), [], 0, save=True)
        animate = animator.run(gif_path)

        gif_path = os.path.join(save_path, 'test_epoch_%d_ind_%d-vq-poc-%d-region.gif' % (epoch, ind, min_index))
        animator = MedicalImageAnimator(x_md_region.to('cpu').detach().numpy().copy(), [], 0, save=True)
        animate = animator.run(gif_path)

        gif_path = os.path.join(save_path, 'test_epoch_%d_ind_%d-vq-poc-%d-mask.gif' % (epoch, ind, min_index))
        animator = MedicalImageAnimator(x_md_mask.to('cpu').detach().numpy().copy(), [], 0, save=True)
        animate = animator.run(gif_path)

        # vox_path = os.path.join(save_path, 'test_epoch_%d_ind_%d-vq-poc-%d-md.nii' % (epoch, ind, min_index))
        # Utils_visualize.save_as_nib(vox_path, output.to('cpu').detach().numpy().copy())

        # Big
        output = model.forwardBig(input_x).squeeze().squeeze()

        gif_path = os.path.join(save_path, 'test_epoch_%d_ind_%d-vq-poc-%d-bg.gif' % (epoch, ind, min_index))
        animator = MedicalImageAnimator(output.to('cpu').detach().numpy().copy(), [], 0, save=True)
        animate = animator.run(gif_path)

        # vox_path = os.path.join(save_path, 'test_epoch_%d_ind_%d-vq-poc-%d-bg.nii' % (epoch, ind, min_index))
        # Utils_visualize.save_as_nib(vox_path, output.to('cpu').detach().numpy().copy())

    @staticmethod
    def drawTSNE(result, result_y, save_name):
        tsne = TSNE(random_state=0, n_components=3)
        tsne_output = tsne.fit_transform(result)
        tsne_output = tsne_output / tsne_output.max() * 2
        print(tsne_output.shape, tsne_output.max(), tsne_output.min())
        tx = tsne_output[:, 0]
        ty = tsne_output[:, 1]
        tz = tsne_output[:, 2]

        images = [Utils_visualize.render_frame(angle,tx,ty,tz,result_y) for angle in range(360)]
        images[0].save(save_name, save_all=True, append_images=images[1:], duration=100, loop=0)

    @staticmethod
    def render_frame(angle, x, y, z, color):
        global data
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(x, y, z, c=color)
        ax.view_init(30, angle)
        plt.close()
        # 軸の設定
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        ax.set_zlim(-3, 3)
        # PIL Image に変換
        buf = BytesIO()
        fig.savefig(buf, bbox_inches='tight', pad_inches=0.0)
        return Image.open(buf)

    @staticmethod
    def VisualizeMain(encoder, model, dataset, save_path, epoch, needPredict, opt):

        # get device
        device = get_device(getattr(opt, 'use_cuda', True))
        
        with torch.no_grad():
            for i, (pos, direct, imp, x_middle, x_big, ind) in enumerate(dataset):
                pos = to_device(pos, device)
                direct = to_device(direct, device)
                imp = to_device(imp, device)
                
                if needPredict and (opt.train_dataset_size - opt.test_dataset_size < ind.item() and ind.item() < opt.train_dataset_size + opt.test_dataset_size):
                    Utils_visualize.drawPredict(encoder, model, pos, direct, imp, x_middle, x_big, ind, epoch, save_path, opt)


                if needPredict and (opt.train_cookbook_size - opt.test_dataset_size < ind.item() and ind.item() < opt.train_cookbook_size):
                    Utils_visualize.drawPredict(encoder, model, pos, direct, imp, x_middle, x_big, ind, epoch, save_path, opt)


