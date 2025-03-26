from torch_geometric.datasets import ShapeNet

# dp = ShapeNet(root='./data/ShapeNet/', categories=['Airplane','Car','Rocket','Table','Motorbike','Animal']).to_datapipe()
dp = ShapeNet(root='./data/ShapeNet/', categories=['Airplane']).to_datapipe()
dp = dp.batch_graphs(batch_size=2, drop_last=True)

test = True

for batch in dp:
    if test:
        print(batch)
        test = False
    pass
