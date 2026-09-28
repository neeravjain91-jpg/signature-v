import sys
sys.path.insert(0, ".")
import torch
from ml.models.siamese_network import SiameseSignatureNet
from ml.preprocessing.signature_preprocessor import SignaturePreprocessor

device = torch.device('cpu')
preproc = SignaturePreprocessor()

# Load Baseline Model
base_chk = torch.load('artifacts/models/best_siamese_model.pt', map_location=device)
model_base = SiameseSignatureNet(embedding_dim=256, backbone='resnet18').to(device)
model_base.load_state_dict(base_chk['model_state_dict'])
model_base.eval()

# Load Champion Model
champ_chk = torch.load('artifacts/models/champion_siamese_model.pt', map_location=device)
model_champ = SiameseSignatureNet(embedding_dim=256, backbone='resnet18').to(device)
model_champ.load_state_dict(champ_chk['model_state_dict'])
model_champ.eval()

ref_path = 'data/raw/signatures/full_org/original_46_1.png'
gen_path = 'data/raw/signatures/full_org/original_46_2.png'
forg_path = 'data/raw/signatures/full_forg/forgeries_46_1.png'

t_ref = preproc.preprocess(ref_path, as_tensor=True).unsqueeze(0).to(device)
t_gen = preproc.preprocess(gen_path, as_tensor=True).unsqueeze(0).to(device)
t_forg = preproc.preprocess(forg_path, as_tensor=True).unsqueeze(0).to(device)

with torch.no_grad():
    res_base_gen = model_base.verify(t_ref, t_gen, threshold=0.7766)
    res_base_forg = model_base.verify(t_ref, t_forg, threshold=0.7766)

    res_champ_gen = model_champ.verify(t_ref, t_gen, threshold=0.7382)
    res_champ_forg = model_champ.verify(t_ref, t_forg, threshold=0.7382)

print('=== BASELINE MODEL (Writer 46 Forensic Case) ===')
print('Threshold:', 0.7766)
print(f"Genuine Pair  (original_46_1 vs original_46_2) -> Dist: {float(res_base_gen['distance']):.4f}, Sim: {float(res_base_gen['similarity_score']):.4f}, Decision: {res_base_gen['decision']}")
print(f"Forgery Pair  (original_46_1 vs forgeries_46_1)-> Dist: {float(res_base_forg['distance']):.4f}, Sim: {float(res_base_forg['similarity_score']):.4f}, Decision: {res_base_forg['decision']}")
print('Separation Margin (Gen Sim - Forg Sim):', f"{float(res_base_gen['similarity_score']) - float(res_base_forg['similarity_score']):.4f}")

print('\n=== CHAMPION MODEL (Writer 46 Forensic Case) ===')
print('Threshold:', 0.7382)
print(f"Genuine Pair  (original_46_1 vs original_46_2) -> Dist: {float(res_champ_gen['distance']):.4f}, Sim: {float(res_champ_gen['similarity_score']):.4f}, Decision: {res_champ_gen['decision']}")
print(f"Forgery Pair  (original_46_1 vs forgeries_46_1)-> Dist: {float(res_champ_forg['distance']):.4f}, Sim: {float(res_champ_forg['similarity_score']):.4f}, Decision: {res_champ_forg['decision']}")
print('Separation Margin (Gen Sim - Forg Sim):', f"{float(res_champ_gen['similarity_score']) - float(res_champ_forg['similarity_score']):.4f}")
