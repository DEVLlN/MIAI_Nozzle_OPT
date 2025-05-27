#include "TMath.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "TH2F.h"

const float GeVtoMeV = 1000.;

TFile *input_file;

TTree *trkHits;
TTree *caloHits;
TTree *muonHits;


TH2F *h01_layout_trk  = new TH2F("h01_layout_trk","Tracker;Z [mm];#rho [mm]",11200,-5600.,5600.,6500,0.,6500.);
TH2F *h01_layout_calo = new TH2F("h01_layout_calo","ECAL and HCAL calorimeters;Z [mm];#rho [mm]",11200,-5600.,5600.,6500,0.,6500.);
TH2F *h01_layout_muon = new TH2F("h01_layout_muon","Muon detectors;Z [mm];#rho [mm]",11200,-5600.,5600.,6500,0.,6500.);

TH2F *h02_layout_VXD = new TH2F("h02_layout_VXD","VXD;Z [mm];#rho [mm]",100,-330.,330.,100,20.,120.);

TH1F *h03_time_vxdB_L0   = new TH1F("h03_time_vxdB_L0","Hit ToA (VXD Barrel L0);T_{reco hit} - T_{0} [ns]",100,-1.,1.);
TH1F *h03_time_itB_L0   = new TH1F("h03_time_itB_L0","Hit ToA (IT Barrel L0);T_{reco hit} - T_{0} [ns]",100,-1.,1.);
TH1F *h03_time_otB_L0   = new TH1F("h03_time_otB_L0","Hit ToA (OT Barrel L0);T_{reco hit} - T_{0} [ns]",100,-1.,1.);

TH1F *h04_energy_vxdB_L0 = new TH1F("h04_energy_vxdB_L0","Hit energy (VXD Barrel L0);E_{reco hit} [MeV]",100.,0.,0.5);
TH1F *h04_energy_itB_L0 = new TH1F("h04_energy_itB_L0","Hit energy (IT Barrel L0);E_{reco hit} [MeV]",100.,0.,0.5);
TH1F *h04_energy_otB_L0 = new TH1F("h04_energy_otB_L0","Hit energy (OT Barrel L0);E_{reco hit} [MeV]",100.,0.,0.5);

TH2F *h05_occupancy_ecalB = new TH2F("h05_occupancy_ecalB",";#theta [rad];#phi [rad]",200,0.59,2.55,200,-3.15,3.15);
TH2F *h06_occupancy_ecalE = new TH2F("h06_occupancy_ecalE",";X [mm];Y [mm]",200,-1800.,1800.,200,-1800.,1800.);
TH2F *h07_depth_ecalB = new TH2F("h07_depth_ecalB",";#theta [rad];#rho [mm]",100,0.55,2.6,50,1490.,1770.);
TH2F *h08_depth_ecalE = new TH2F("h08_depth_ecalE",";Z [mm];Y [mm]",40,2300.,2515.,50,-1800.,1800.);

TH2F *h09_occupancy_hcalB = new TH2F("h09_occupancy_hcalB",";#theta [rad];#phi [rad]",100,0.66,2.47,100,-3.15,3.15);
TH2F *h10_occupancy_hcalE = new TH2F("h10_occupancy_hcalE",";X [mm];Y [mm]",100,-3000.,3000.,100,-3000.,3000.);
TH2F *h11_depth_hcalB = new TH2F("h11_depth_hcalB",";#theta [rad];#rho [mm]",50,0.6,2.55,60,1700.,3500.);
TH2F *h12_depth_hcalE = new TH2F("h12_depth_hcalE",";Z [mm];Y [mm]",60,2500.,4180.,50,-3100,3100.);

TH1F *h13_time_ecalB   = new TH1F("h13_time_ecalB","Hit ToA (ECAL Barrel);T_{reco hit} - T_{0} [ns]",100,-1.,10.);
TH1F *h14_time_hcalB   = new TH1F("h14_time_hcalB","Hit ToA (HCAL Barrel);T_{reco hit} - T_{0} [ns]",100,-1.,10.);

TH1F *h15_energy_ecalB = new TH1F("h15_energy_ecalB","Hit energy (ECAL Barrel);E_{reco hit} [GeV]",100.,0.,1.);
TH1F *h16_energy_hcalB = new TH1F("h16_energy_hcalB","Hit energy (HCAL Barrel);E_{reco hit} [GeV]",100.,0.,1.);



void make_recoHitPlots_BIB(const TString filename="/data/ntuples/BIB/allHits_ntuple_BIB.root"){

  input_file = new TFile(filename, "read");
  
  trkHits  = (TTree*) input_file->Get("TrackerHitsTuple");
  caloHits = (TTree*) input_file->Get("CaloHitsTuple");
  muonHits = (TTree*) input_file->Get("MuonHitsTuple");

  
  // ================================================================================================
  // --- tracker hits

  int trk_n;
  int *trk_id0 = new int[10000];
  double *trk_x = new double[10000];
  double *trk_y = new double[10000];
  double *trk_z = new double[10000];
  float *trk_t = new float[10000];
  float *trk_e = new float[10000];

  trkHits->SetBranchAddress("ntrh",&trk_n);
  trkHits->SetBranchAddress("thci0",trk_id0);
  trkHits->SetBranchAddress("thpox",trk_x);
  trkHits->SetBranchAddress("thpoy",trk_y);
  trkHits->SetBranchAddress("thpoz",trk_z);
  trkHits->SetBranchAddress("thtim",trk_t);
  trkHits->SetBranchAddress("thedp",trk_e);
    
  for(int ientry=0; ientry<trkHits->GetEntries(); ++ientry){
    //for(int ientry=0; ientry<1; ++ientry){

    trkHits->GetEntry(ientry);

    for (int ihit=0; ihit<trk_n; ++ihit){

      // CellID encoding: "system:5,side:-2,layer:6,module:11,sensor:8"
      const unsigned int system = (unsigned) ( trk_id0[ihit] & 0x1f );
      const int side = (int) ( (trk_id0[ihit] >> 5) & 0x3 );
      const unsigned int layer = (unsigned) ( (trk_id0[ihit] >> 7) & 0x3f );

      float rho = sqrt(trk_x[ihit]*trk_x[ihit]+trk_y[ihit]*trk_y[ihit]);
      h01_layout_trk->Fill(trk_z[ihit],rho);

      
      // --- VXD barrel
      if ( system==1 ) {

	h02_layout_VXD->Fill(trk_z[ihit],rho);

	if( layer==0 ){
	  h03_time_vxdB_L0->Fill(trk_t[ihit]);
	  h04_energy_vxdB_L0->Fill(trk_e[ihit]*GeVtoMeV);
	}

      }

      
      // --- VXD endcap
      if ( system==2 )
      	h02_layout_VXD->Fill(trk_z[ihit],rho);

      
      // --- IT barrel
      if ( system==3 ) {

	if( layer==0 ){
	  h03_time_itB_L0->Fill(trk_t[ihit]);
	  h04_energy_itB_L0->Fill(trk_e[ihit]*GeVtoMeV);
	}

      }

      
      // --- OT barrel
      if ( system==5 ) {

	if( layer==0 ){
	  h03_time_otB_L0->Fill(trk_t[ihit]);
	  h04_energy_otB_L0->Fill(trk_e[ihit]*GeVtoMeV);
	}

      }

      
    } // ihit loop

    
  } // trkHits ientry loop

  delete [] trk_id0;
  delete [] trk_x;
  delete [] trk_y;
  delete [] trk_z;
  delete [] trk_t;
  delete [] trk_e;
    

  // ================================================================================================
  // --- calorimeter hits

  int calo_n;
  int *calo_id0 = new int[15000];
  float *calo_x = new float[15000];
  float *calo_y = new float[15000];
  float *calo_z = new float[15000];
  float *calo_t = new float[15000];
  float *calo_e = new float[15000];

  caloHits->SetBranchAddress("ncah",&calo_n);
  caloHits->SetBranchAddress("caci0",calo_id0);
  caloHits->SetBranchAddress("capox",calo_x);
  caloHits->SetBranchAddress("capoy",calo_y);
  caloHits->SetBranchAddress("capoz",calo_z);
  caloHits->SetBranchAddress("catim",calo_t);
  caloHits->SetBranchAddress("caene",calo_e);
    
  for(int ientry=0; ientry<caloHits->GetEntries(); ++ientry){

    caloHits->GetEntry(ientry);

    for (int ihit=0; ihit<calo_n; ++ihit){

      // CellID encoding: "system:5,side:-2,module:8,stave:4,layer:9,submodule:4,x:32:-16,y:-16"
      const unsigned int system = (unsigned) ( calo_id0[ihit] & 0x1f );
      const int side = (int) ( (calo_id0[ihit] >> 5) & 0x3 );
      
      float rho = sqrt(calo_x[ihit]*calo_x[ihit]+calo_y[ihit]*calo_y[ihit]);

      h01_layout_calo->Fill(calo_z[ihit],rho);

      
      float phi   = TMath::ATan2(calo_y[ihit], calo_x[ihit]);
      float theta = TMath::ATan2(rho, calo_z[ihit]);

      
      // --- ECAL barrel
      if ( system==20 ){
	
	h05_occupancy_ecalB->Fill(theta,phi);
	h07_depth_ecalB->Fill(theta,rho);
	h13_time_ecalB->Fill(calo_t[ihit]);	
	h15_energy_ecalB->Fill(calo_e[ihit]);	

      }


      // --- ECAL endcap
      if ( system==29  && side==1 ){

	h06_occupancy_ecalE->Fill(calo_y[ihit], calo_x[ihit]);
	h08_depth_ecalE->Fill(calo_z[ihit],calo_y[ihit]);
	
      }


      
      // --- HCAL barrel
      if ( system==10 ){

	h09_occupancy_hcalB->Fill(theta,phi);
	h11_depth_hcalB->Fill(theta,rho);
	h14_time_hcalB->Fill(calo_t[ihit]);	
	h16_energy_hcalB->Fill(calo_e[ihit]);	
	
      }


      // --- HCAL endcap
      if ( system==11  && side==1 ){

	h10_occupancy_hcalE->Fill(calo_y[ihit], calo_x[ihit]);
	h12_depth_hcalE->Fill(calo_z[ihit],calo_y[ihit]);
	
      }

      
    } // ihit loop

    
  } // caloHits ientry loop

  delete [] calo_id0;
  delete [] calo_x;
  delete [] calo_y;
  delete [] calo_z;
  delete [] calo_t;
  delete [] calo_e;
    

  // ================================================================================================
  // --- muon detector hits

  int muon_n;
  int *muon_id0 = new int[1000];
  float *muon_x = new float[1000];
  float *muon_y = new float[1000];
  float *muon_z = new float[1000];
  float *muon_t = new float[1000];
  float *muon_e = new float[1000];

  muonHits->SetBranchAddress("ncah",&muon_n);
  muonHits->SetBranchAddress("caci0",muon_id0);
  muonHits->SetBranchAddress("capox",muon_x);
  muonHits->SetBranchAddress("capoy",muon_y);
  muonHits->SetBranchAddress("capoz",muon_z);
  muonHits->SetBranchAddress("catim",muon_t);
  muonHits->SetBranchAddress("caene",muon_e);
    
  for(int ientry=0; ientry<muonHits->GetEntries(); ++ientry){

    muonHits->GetEntry(ientry);

    for (int ihit=0; ihit<muon_n; ++ihit){

      // CellID encoding: "system:5,side:-2,module:8,stave:4,layer:9,submodule:4,x:32:-16,y:-16"
      const unsigned int system = (unsigned) ( muon_id0[ihit] & 0x1f );
      const int side = (int) ( (muon_id0[ihit] >> 5) & 0x3 );
      
      float rho = sqrt(muon_x[ihit]*muon_x[ihit]+muon_y[ihit]*muon_y[ihit]);

      h01_layout_muon->Fill(muon_z[ihit],rho);
      
    } // ihit loop

    
  } // muonHits ientry loop

  delete [] muon_id0;
  delete [] muon_x;
  delete [] muon_y;
  delete [] muon_z;
  delete [] muon_t;
  delete [] muon_e;
    

  // ================================================================================================

  h03_time_vxdB_L0->SetLineColor(2);
  h03_time_itB_L0 ->SetLineColor(4);
  h03_time_otB_L0 ->SetLineColor(1);

  h04_energy_vxdB_L0->SetLineColor(2);
  h04_energy_itB_L0 ->SetLineColor(4);
  h04_energy_otB_L0 ->SetLineColor(1);

}
