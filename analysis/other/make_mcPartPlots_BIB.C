#include "TMath.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1I.h"
#include "TH1F.h"
#include "TH2F.h"

TFile *input_file;

TTree *partBIB;

TH2F *h01_entryPoint = new TH2F("h01_entryPoint","BIB entry point;z_{v} [mm];#sqrt{x_{v}^{2}+y_{v}^{2}}",
				2000,-8000.,8000.,500,0.,4000);
TH1F *h02_entryZ_ph = new TH1F("h02_entryZ_ph","BIB photons entry point Z;z_{#gamma} [mm]",100.,-8000.,8000.);
TH1F *h02_entryZ_e  = new TH1F("h02_entryZ_e","BIB electrons entry point Z;z_{e} [mm]",100.,-8000.,8000.);
TH1F *h02_entryZ_mu = new TH1F("h02_entryZ_mu","BIB muons entry point Z;z_{#mu} [mm]",100.,-8000.,8000.);
TH1F *h02_entryZ_n  = new TH1F("h02_entryZ_n","BIB neutron entry point Z;z_{n} [mm]",100.,-8000.,8000.);
TH1F *h02_entryZ_h  = new TH1F("h02_entryZ_h","BIB hadrons entry point Z;z_{h} [mm]",100.,-8000.,8000.);

TH1F *h03_p_ph = new TH1F("h03_p_ph","BIB photons entry point Z;p_{#gamma} [GeV]",100.,0.,0.2);
TH1F *h03_p_e  = new TH1F("h03_p_e","BIB electrons momentum;p_{e} [GeV]",100.,0.,0.2);
TH1F *h05_p_mu = new TH1F("h04_p_mu","BIB muons momentum;p_{#mu} [GeV]",50.,0.,10.);
TH1F *h04_p_n  = new TH1F("h04_p_n","BIB neutron momentum;p_{n} [GeV]",100.,0.,3.);
TH1F *h04_p_h  = new TH1F("h05_p_h","BIB hadrons momentum;p_{h} [GeV]",100.,0.,3.);

TH1F *h06_T_ph = new TH1F("h06_T_ph","BIB photons ToA;T_{#gamma} - T_{0} [ns]",100.,-25.,25.);
TH1F *h06_T_e  = new TH1F("h06_T_e","BIB electrons ToA;T_{e} - T_{0} [ns]",100.,-25.,25.);
TH1F *h06_T_mu = new TH1F("h06_T_mu","BIB muons ToA;T_{#mu} - T_{0} [ns]",100.,-25.,25.);
TH1F *h06_T_n  = new TH1F("h06_T_n","BIB neutrons ToA;T_{n} - T_{0} [ns]",100.,-25.,25.);
TH1F *h06_T_h  = new TH1F("h06_T_h","BIB hadrons ToA;T_{e} - T_{0} [ns]",100.,-25.,25.);


void make_mcPartPlots_BIB(const TString filename="/data/ntuples/BIB/mcParts_ntuple_BIB.root"){

  input_file = new TFile(filename, "read");

  partBIB = (TTree*) input_file->Get("MCpartTuple");
  

  // ================================================================================================

  int n_part;
  int *p_pdg = new int[100000];
  int *p_genCode = new int[100000];
  float *p_vx = new float[100000];
  float *p_vy = new float[100000];
  float *p_vz = new float[100000];
  float *p_px = new float[100000];
  float *p_py = new float[100000];
  float *p_pz = new float[100000];
  float *p_t  = new float[100000];

  partBIB->SetBranchAddress("nmcp", &n_part);
  partBIB->SetBranchAddress("mcpdg", p_pdg);
  partBIB->SetBranchAddress("mcgst", p_genCode);
  partBIB->SetBranchAddress("mcvtx", p_vx);
  partBIB->SetBranchAddress("mcvty", p_vy);
  partBIB->SetBranchAddress("mcvtz", p_vz);
  partBIB->SetBranchAddress("mcmox", p_px);
  partBIB->SetBranchAddress("mcmoy", p_py);
  partBIB->SetBranchAddress("mcmoz", p_pz);
  partBIB->SetBranchAddress("mctim", p_t);

  for(int ientry=0; ientry<partBIB->GetEntries(); ++ientry){

    partBIB->GetEntry(ientry);

    for (int ipart=0; ipart<n_part; ++ipart) {

      // --- select only the primary BIB particles
      if ( p_genCode[ipart]!=1 ) continue;


      // --- skip the neutrinos
      if ( fabs(p_pdg[ipart])==12 ||
	   fabs(p_pdg[ipart])==14 ||
	   fabs(p_pdg[ipart])==16 ) continue;

      
      float rho = sqrt(p_vx[ipart]*p_vx[ipart]+p_vy[ipart]*p_vy[ipart]);
      h01_entryPoint->Fill(p_vz[ipart], rho);

      float mom = sqrt(p_px[ipart]*p_px[ipart]+
		       p_py[ipart]*p_py[ipart]+
		       p_pz[ipart]*p_pz[ipart]);

      // --- photons
      if ( fabs(p_pdg[ipart]) == 22 ){
	h02_entryZ_ph->Fill(p_vz[ipart]);
	h03_p_ph->Fill(mom);
	h06_T_ph->Fill(p_t[ipart]);
      }

      // --- electrons and positrons
      else if ( fabs(p_pdg[ipart]) == 11 ){
	h02_entryZ_e->Fill(p_vz[ipart]);
	h03_p_e->Fill(mom);
	h06_T_e->Fill(p_t[ipart]);
      }

      // --- muons and antimuons
      else if ( fabs(p_pdg[ipart]) == 13 ){
	h02_entryZ_mu->Fill(p_vz[ipart]);
	h05_p_mu->Fill(mom);
	h06_T_mu->Fill(p_t[ipart]);
      }

      // --- neutrons
      else if ( fabs(p_pdg[ipart]) == 2112 ){
	h02_entryZ_n->Fill(p_vz[ipart]);
	h04_p_n->Fill(mom);
	h06_T_n->Fill(p_t[ipart]);
      }

      // --- other hadrons
      else {
	h02_entryZ_h->Fill(p_vz[ipart]);
	h04_p_h->Fill(mom);
	h06_T_h->Fill(p_t[ipart]);
      }

    } // ipart loop
    
  } // mcParts ientry loop

  delete [] p_pdg;
  delete [] p_genCode;
  delete [] p_vx;
  delete [] p_vy;
  delete [] p_vz;
  delete [] p_px;
  delete [] p_py;
  delete [] p_pz;

  // ================================================================================================

  h02_entryZ_ph->SetLineColor(2);
  h02_entryZ_e ->SetLineColor(1);
  h02_entryZ_mu->SetLineColor(3);
  h02_entryZ_n ->SetLineColor(4);
  h02_entryZ_h ->SetLineColor(6);

  h03_p_ph->SetLineColor(2);
  h03_p_e ->SetLineColor(1);
  h05_p_mu->SetLineColor(3);
  h04_p_n ->SetLineColor(4);
  h04_p_h ->SetLineColor(6);

  h06_T_ph->SetLineColor(2);
  h06_T_e ->SetLineColor(1);
  h06_T_mu->SetLineColor(3);
  h06_T_n ->SetLineColor(4);
  h06_T_h ->SetLineColor(6);
  
}
