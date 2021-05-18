import os
import torch
import torchvision
import numpy as np
import imageio
import json
import cv2


trans_t = lambda t : torch.tensor([[1, 0, 0, 0],
                                   [0, 1, 0, 0],
                                   [0, 0, 1, t],
                                   [0, 0, 0, 1]], dtype=torch.float32)

rot_phi = lambda phi : torch.tensor([[1, 0, 0, 0],
                                     [0, np.cos(phi), -np.sin(phi), 0],
                                     [0, np.sin(phi), np.cos(phi), 0],
                                     [0, 0, 0, 1]], dtype=torch.float32)

rot_theta = lambda th : torch.tensor([[np.cos(th), 0, -np.sin(th), 0],
                                      [0, 1, 0, 0],
                                      [np.sin(th), 0, np.cos(th), 0],
                                      [0, 0, 0, 1]], dtype=torch.float32)

def pose_spherical(theta, phi, radius):
    c2w = torch.Tensor(np.array([[-1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]])) @\
     rot_theta(theta/180.0*np.pi) @ rot_phi(phi/180.0*np.pi) @ trans_t(radius)
    return c2w

def load_blender_data(basedir, half_res = False, testskip = 1):
    splits = ['train', 'val', 'test']
    metas = {}
    for s in splits:
        with open(os.path.join(basedir, 'transforms_{}.json'.format(s)), 'r') as fp:
            metas[s] = json.load(fp)

    all_imgs = []
    all_poses = []
    counts = [0]
    for s in splits:
        meta = metas[s]
        imgs = []
        poses = []
        if s == 'train' or testskip == 0:
            skip = 1
        else:
            skip = testskip

        for frame in meta['frames'][::skip]:
            fname = os.path.join(basedir, frame['file_path'] + '.png')
            imgs.append(imageio.imread(fname))
            poses.append(np.array(frame['transform_matrix']))
        imgs = (np.array(imgs) / 255.0).astype(np.float32)
        poses = np.array(poses).astype(np.float32)
        counts.append(counts[-1] + imgs.shape[0])
        all_imgs.append(imgs)
        all_poses.append(poses)

    i_split = [np.arange(counts[i], counts[i+1]) for i in range(3)]

    imgs = np.concatenate(all_imgs, 0)
    poses = np.concatenate(all_poses, 0)

    H, W = imgs[0].shape[:2]
    camera_angle_x = float(meta['camera_angle_x'])
    focal = .5 * W / np.tan(.5 * camera_angle_x)

    render_poses = torch.stack([pose_spherical(angle, -30.0, 4.0) for angle in np.linspace(-180, 180, 41)[:-1]], dim=0)

    if half_res:
        #m = torch.nn.AvgPool2d(2)
        #for idx in range(imgs.shape[0]):
        #    imgs[idx,:,:,:] = m(imgs[idx])
        
        H, W = imgs[0].shape[:2]
        focal = focal/2.0

        imgs_half_res = np.zeros((imgs.shape[0], H, W, 4))
        for i, img in enumerate(imgs):
            imgs_half_res[i] = cv2.resize(img, (H, W), interpolation=cv2.INTER_AREA)
            imgs = imgs_half_res

        #H, W = imgs[0].shape[:2]
        #focal = focal / 2.0

    return imgs, poses, render_poses, [H, W, focal], i_split
