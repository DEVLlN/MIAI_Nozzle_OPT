Beam-induced background (BIB) characterization

=========================================================================

I - A look at the MC truth of BIB particles

To fill the histograms:

root -l make_mcPartPlots_BIB.C+


1) BIB particle entry point into the detector:

h01_entryPoint->Draw("COLZ")


2) z coordinates of entry point for different particles species:

h02_entryZ_ph->Draw();
h02_entryZ_e->Draw("SAME");
h02_entryZ_n->Draw("SAME");
h02_entryZ_h->Draw("SAME");
h02_entryZ_mu->Draw("SAME");
c1->SetLogy();


3) Photons and elecrons momenta:

h03_p_ph->Draw();
h03_p_e->Draw("SAME");


4) Neutrons and other hadrons momenta:

h04_p_n->Draw();
h04_p_h->Draw("SAME");


5) Muons momenta:

h05_p_mu->Draw();


6) Time of arrival at the detector entry point w.r.t. the bunch crossing:

h06_T_ph->Draw();
h06_T_e->Draw("SAME");
h06_T_n->Draw("SAME");
h06_T_h->Draw("SAME");
h06_T_mu->Draw("SAME");


=========================================================================

II - A look at the reconstructed detector hits of the BIB particles

To fill the histograms:

root -l make_recoHitPlots_BIB.C+


1) Distributions of the tracker, calorimeters and muon detectors hits in the rho-z plane:

h01_layout_trk->Draw("COLZ");
h01_layout_calo->Draw("COLZ,SAME");
h01_layout_muon->Draw("COLZ,SAME");


2) Distributions of the vertex detector hits in the rho-z plane:

h02_layout_VXD->Draw("COLZ");


3) Hit times w.r.t. the bunch crossing at the first layers of the vertex detector
   and the inner and outer trackers:

h03_time_itB_L0->Draw();
h03_time_otB_L0->Draw("SAME");
h03_time_vxdB_L0->Draw("SAME");


4) Hit energies deposited on the first layers of the vertex detector and the
   inner and outer trackers:

h04_energy_vxdB_L0->Draw();
h04_energy_itB_L0->Draw("SAME");
h04_energy_otB_L0->Draw("SAME");


5) ECAL barrel and ECAL+ endcap hit occupancies in the phi-theta and y-x planes:

h05_occupancy_ecalB->Draw("COLZ");
h06_occupancy_ecalE->Draw("COLZ");


6) ECAL barrel and ECAL+ endcap hit occupancies in the rho-theta and y-z planes:

h07_depth_ecalB->Draw("COLZ");
h08_depth_ecalE->Draw("COLZ");


7) HCAL barrel and HCAL+ endcap hit occupancies in the phi-theta and y-x planes:

h09_occupancy_hcalB->Draw("COLZ");
h10_occupancy_hcalE->Draw("COLZ");


8) HCAL barrel and HCAL+ endcap hit occupancies in the rho-theta and y-z planes:

h11_depth_hcalB->Draw("COLZ");
h12_depth_hcalE->Draw("COLZ");


9) Hit times at the ECAL and HCAL barrels:

h13_time_ecalB->Draw();
h14_time_hcalB->Draw();


10) Hit energies depositid in the ECAL and HCAL barrels:

h15_energy_ecalB->Draw();
c1->SetLogy();
h16_energy_hcalB->Draw();


=========================================================================
