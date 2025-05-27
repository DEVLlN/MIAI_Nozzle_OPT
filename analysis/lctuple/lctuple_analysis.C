#include <iostream>
#include "TString.h"
#include "TFile.h"
#include "TTree.h"
#include "TH1F.h"
#include "Math/Vector4D.h"


// --- Histogram declaration

TH1F* h_mc_pdg;
TH1F* h_reco_pdg;
TH1F* h_jet_n;
TH1F* h_dijet_m;


// ===========================================================================

void lctuple_analysis( const TString filename="lctuple_example.root", const long int maxEvents=-1 ){

  // --- Histogram booking

  h_mc_pdg = new TH1F("h_mc_pdg","Stable MC particles; PDG code", 4500, -2250., 2250.);
  h_reco_pdg = new TH1F("h_reco_pdg","Reconstructed particles; PDG code", 4500, -2250., 2250.);
  h_jet_n = new TH1F("h_jet_n","Reconstructed jets; N_{jet}",10, 0., 10.);
  h_dijet_m = new TH1F("h_dijet_m","Dijet mass; m_{12} [GeV]",100, 110., 140.);

  
  //  --- Open the ntuple file and get the tree
   
  TFile* input_file = new TFile(filename.Data(), "read");

  TTree* myLCTuple = (TTree*) input_file->Get("MyLCTuple");


  // --- Loop over the ntuple entries
  

  // --- MC particles
  int n_mcp;
  int *mcp_pdg  = new int[1500000];
  int *mcp_genCode = new int[1500000];
  int *mcp_simCode = new int[1500000];
  float *mcp_vx = new float[1500000];
  float *mcp_vy = new float[1500000];
  float *mcp_vz = new float[1500000];
  float *mcp_px = new float[1500000];
  float *mcp_py = new float[1500000];
  float *mcp_pz = new float[1500000];
  float *mcp_ene = new float[1500000];
  float *mcp_q  = new float[1500000];
  float *mcp_t  = new float[1500000];

  myLCTuple->SetBranchAddress("nmcp", &n_mcp);
  myLCTuple->SetBranchAddress("mcpdg", mcp_pdg);
  myLCTuple->SetBranchAddress("mcgst", mcp_genCode); 
  myLCTuple->SetBranchAddress("mcsst", mcp_simCode); 
  myLCTuple->SetBranchAddress("mcvtx", mcp_vx);
  myLCTuple->SetBranchAddress("mcvty", mcp_vy);
  myLCTuple->SetBranchAddress("mcvtz", mcp_vz);
  myLCTuple->SetBranchAddress("mcmox", mcp_px);
  myLCTuple->SetBranchAddress("mcmoy", mcp_py);
  myLCTuple->SetBranchAddress("mcmoz", mcp_pz);
  myLCTuple->SetBranchAddress("mcene", mcp_ene);
  myLCTuple->SetBranchAddress("mccha", mcp_q);
  myLCTuple->SetBranchAddress("mctim", mcp_t);


  // --- RECO particles
  int n_reco;
  int *reco_type  = new int[1000];
  float *reco_px  = new float[1000];
  float *reco_py  = new float[1000];
  float *reco_pz  = new float[1000];
  float *reco_ene = new float[1000];
  float *reco_q   = new float[1000];

  myLCTuple->SetBranchAddress("nrec", &n_reco);
  myLCTuple->SetBranchAddress("rctyp", reco_type);
  myLCTuple->SetBranchAddress("rcmox", reco_px);
  myLCTuple->SetBranchAddress("rcmoy", reco_py);
  myLCTuple->SetBranchAddress("rcmoz", reco_pz);
  myLCTuple->SetBranchAddress("rcene", reco_ene);
  myLCTuple->SetBranchAddress("rccha", reco_q);


  // --- RECO jets
  int n_jet;
  float *jet_px  = new float[1000];
  float *jet_py  = new float[1000];
  float *jet_pz  = new float[1000];
  float *jet_ene = new float[1000];
  float *jet_q   = new float[1000];

  myLCTuple->SetBranchAddress("njet", &n_jet);
  myLCTuple->SetBranchAddress("jmox", jet_px);
  myLCTuple->SetBranchAddress("jmoy", jet_py);
  myLCTuple->SetBranchAddress("jmoz", jet_pz);
  myLCTuple->SetBranchAddress("jene", jet_ene);
  myLCTuple->SetBranchAddress("jcha", jet_q);


  const long int nEntries = ( maxEvents < 0 ? myLCTuple->GetEntries() : maxEvents );
  for(int ientry=0; ientry<nEntries; ++ientry){

    if ( ientry % 1000 == 0 )
      std::cout << ientry << " / " << nEntries << endl;

    myLCTuple->GetEntry(ientry);

    // --- loop over the Monte Carlo particles
    for (int imc=0; imc<n_mcp; ++imc){

      // --- keep only the stable particles
      if ( mcp_genCode[imc] != 1 ) continue;

      h_mc_pdg->Fill(mcp_pdg[imc]);

    } // imc loop
    
    
    // --- loop over the reconstructed particles
    for (int ireco=0; ireco<n_reco; ++ireco){

      h_reco_pdg->Fill(reco_type[ireco]);

    } // ireco loop
    
    h_jet_n->Fill(n_jet);
    
    // --- select events with two reconstructed jets
    if ( n_jet != 2 ) continue; 

    ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<float> > p_j1(jet_px[0],jet_py[0],jet_pz[0],jet_ene[0]);
    ROOT::Math::LorentzVector<ROOT::Math::PxPyPzE4D<float> > p_j2(jet_px[1],jet_py[1],jet_pz[1],jet_ene[1]);

    float dijet_mass = (p_j1+p_j2).M();

    h_dijet_m->Fill(dijet_mass);
    

  } // ientry loop
  
  // =========================================================================

  //  --- Clean up the heap

  delete [] mcp_pdg;
  delete [] mcp_genCode;
  delete [] mcp_simCode;
  delete [] mcp_vx;
  delete [] mcp_vy;
  delete [] mcp_vz;
  delete [] mcp_px;
  delete [] mcp_py;
  delete [] mcp_pz;
  delete [] mcp_q;
  delete [] mcp_t;
    
  delete [] reco_type;
  delete [] reco_px;
  delete [] reco_py;
  delete [] reco_pz;
  delete [] reco_ene;
  delete [] reco_q;
  
  delete [] jet_px;
  delete [] jet_py;
  delete [] jet_pz;
  delete [] jet_ene;
  delete [] jet_q;


  // --- Close the ntuple file

  input_file->Close();
 
}

