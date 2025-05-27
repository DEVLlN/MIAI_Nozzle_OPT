//This is a simple macro to measure the pt resolution for signal+BIB and the signal only
//It relies on the MyTrackChecker/checktree variables
//Cuts on the maximum chi2 and the minimum number of hits can be set as external parameters

void track_pt_resolution(){

  //Input files are loaded

  TChain* c_sig_and_BIB = new TChain("c_sig_and_BIB");
  c_sig_and_BIB->Add("/data/ntuples/signal_BIB/histograms_sig_and_BIB_070_090.root/MyTrackChecker/checktree"); 

  TChain* c_sig_only = new TChain("c_sig_only");
  c_sig_only->Add("/data/ntuples/signal/histograms_sig_only_070_090.root/MyTrackChecker/checktree"); 

  //Tree variables are set

  std::vector<double> *pt_true=0;
  std::vector<double> *phi_true=0;
  std::vector<double> *theta_true=0;
  std::vector<double> *d0_true=0;
  std::vector<double> *tanlambda_true=0;
  std::vector<double> *z0_true=0;
  std::vector<double> *pt_reco=0;
  std::vector<double> *phi_reco=0;
  std::vector<double> *theta_reco=0;
  std::vector<double> *d0_reco=0;
  std::vector<double> *z0_reco=0;
  std::vector<double> *tanlambda_reco=0;
  std::vector<int> *trueID=0;
  std::vector<double> *omega_pull=0;
  std::vector<double> *phi_pull=0;
  std::vector<double> *d0_pull=0;
  std::vector<double> *z0_pull=0;
  std::vector<double> *tanlambda_pull=0;
  std::vector<int> *reco_Nhits=0;
  std::vector<double> *reco_Chi2OverNDF=0;

  std::vector<double> *resOmega=0;
  std::vector<double> *resPhi=0;
  std::vector<double> *resTanLambda=0;
  std::vector<double> *resD0=0;
  std::vector<double> *resZ0=0;

  c_sig_and_BIB->SetBranchAddress("resOmega", &resOmega);
  c_sig_and_BIB->SetBranchAddress("resPhi", &resPhi);
  c_sig_and_BIB->SetBranchAddress("resTanLambda", &resTanLambda);
  c_sig_and_BIB->SetBranchAddress("resD0", &resD0);
  c_sig_and_BIB->SetBranchAddress("resZ0", &resZ0);

  c_sig_and_BIB->SetBranchAddress("truePt", &pt_true);
  c_sig_and_BIB->SetBranchAddress("truePhi", &phi_true);
  c_sig_and_BIB->SetBranchAddress("trueTheta", &theta_true);
  c_sig_and_BIB->SetBranchAddress("trueD0", &d0_true);
  c_sig_and_BIB->SetBranchAddress("trueZ0", &z0_true);
  c_sig_and_BIB->SetBranchAddress("recoPt", &pt_reco);
  c_sig_and_BIB->SetBranchAddress("recoPhi", &phi_reco);
  c_sig_and_BIB->SetBranchAddress("recoTheta", &theta_reco);
  c_sig_and_BIB->SetBranchAddress("recoD0", &d0_reco);
  c_sig_and_BIB->SetBranchAddress("recoZ0", &z0_reco);

  c_sig_and_BIB->SetBranchAddress("trueID", &trueID);

  c_sig_and_BIB->SetBranchAddress("recoPt", &pt_reco);
  c_sig_and_BIB->SetBranchAddress("recoPhi", &phi_reco);
  c_sig_and_BIB->SetBranchAddress("recoD0", &d0_reco);
  c_sig_and_BIB->SetBranchAddress("recoZ0", &z0_reco);

  c_sig_and_BIB->SetBranchAddress("pullOmega", &omega_pull);
  c_sig_and_BIB->SetBranchAddress("pullPhi", &phi_pull);
  c_sig_and_BIB->SetBranchAddress("pullD0", &d0_pull);
  c_sig_and_BIB->SetBranchAddress("pullZ0", &z0_pull);
  c_sig_and_BIB->SetBranchAddress("pullTanLambda", &tanlambda_pull);

  c_sig_and_BIB->SetBranchAddress("recoNhits", &reco_Nhits);
  c_sig_and_BIB->SetBranchAddress("recoChi2OverNDF", &reco_Chi2OverNDF); 

  c_sig_only->SetBranchAddress("resOmega", &resOmega);
  c_sig_only->SetBranchAddress("resPhi", &resPhi);
  c_sig_only->SetBranchAddress("resTanLambda", &resTanLambda);
  c_sig_only->SetBranchAddress("resD0", &resD0);
  c_sig_only->SetBranchAddress("resZ0", &resZ0);

  c_sig_only->SetBranchAddress("truePt", &pt_true);
  c_sig_only->SetBranchAddress("truePhi", &phi_true);
  c_sig_only->SetBranchAddress("trueTheta", &theta_true);
  c_sig_only->SetBranchAddress("trueD0", &d0_true);
  c_sig_only->SetBranchAddress("trueZ0", &z0_true);
  c_sig_only->SetBranchAddress("recoPt", &pt_reco);
  c_sig_only->SetBranchAddress("recoPhi", &phi_reco);
  c_sig_only->SetBranchAddress("recoTheta", &theta_reco);
  c_sig_only->SetBranchAddress("recoD0", &d0_reco);
  c_sig_only->SetBranchAddress("recoZ0", &z0_reco);

  c_sig_only->SetBranchAddress("trueID", &trueID);

  c_sig_only->SetBranchAddress("recoPt", &pt_reco);
  c_sig_only->SetBranchAddress("recoPhi", &phi_reco);
  c_sig_only->SetBranchAddress("recoD0", &d0_reco);
  c_sig_only->SetBranchAddress("recoZ0", &z0_reco);

  c_sig_only->SetBranchAddress("pullOmega", &omega_pull);
  c_sig_only->SetBranchAddress("pullPhi", &phi_pull);
  c_sig_only->SetBranchAddress("pullD0", &d0_pull);
  c_sig_only->SetBranchAddress("pullZ0", &z0_pull);
  c_sig_only->SetBranchAddress("pullTanLambda", &tanlambda_pull);

  c_sig_only->SetBranchAddress("recoNhits", &reco_Nhits);
  c_sig_only->SetBranchAddress("recoChi2OverNDF", &reco_Chi2OverNDF); 

  //Histograms are prepared

  TH1F* h_pt_reso_sig_and_BIB = new TH1F("h_pt_reso_sig_and_BIB",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_only = new TH1F("h_pt_reso_sig_only",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);

  TH1F* h_pt_reso_sig_and_BIB_pt_00_25 = new TH1F("h_pt_reso_sig_and_BIB_pt_00_25",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_and_BIB_pt_25_50 = new TH1F("h_pt_reso_sig_and_BIB_pt_25_50",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_and_BIB_pt_50_75 = new TH1F("h_pt_reso_sig_and_BIB_pt_50_75",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_and_BIB_pt_75_100 = new TH1F("h_pt_reso_sig_and_BIB_pt_75_100",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);

  TH1F* h_pt_reso_sig_only_pt_00_25 = new TH1F("h_pt_reso_sig_only_pt_00_25",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_only_pt_25_50 = new TH1F("h_pt_reso_sig_only_pt_25_50",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_only_pt_50_75 = new TH1F("h_pt_reso_sig_only_pt_50_75",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);
  TH1F* h_pt_reso_sig_only_pt_75_100 = new TH1F("h_pt_reso_sig_only_pt_75_100",";#frac{#Delta p_{T}}{p_{T}}",40,-0.05,0.05);

  //Loop on the events for signal+BIB

  for(unsigned int ientry=0; ientry<c_sig_and_BIB->GetEntries(); ++ientry){

   c_sig_and_BIB->GetEntry(ientry);

   //Loop on the tracks 

   for (unsigned int itrk=0; itrk<pt_reco->size(); ++itrk){

      //Cuts are applied

      if (reco_Chi2OverNDF->at(itrk)>5) continue;
      if (reco_Nhits->at(itrk)<6) continue;

      //Histograms are filled

      if(abs(trueID->at(itrk))==13) {
        h_pt_reso_sig_and_BIB->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>0.0 && pt_reco->at(itrk)<2.5) h_pt_reso_sig_and_BIB_pt_00_25->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>2.5 && pt_reco->at(itrk)<5.0) h_pt_reso_sig_and_BIB_pt_25_50->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>5.0 && pt_reco->at(itrk)<7.5) h_pt_reso_sig_and_BIB_pt_50_75->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>7.5 && pt_reco->at(itrk)<10.) h_pt_reso_sig_and_BIB_pt_75_100->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        }
      }
    }

  //Loop on the events for signal only

  for(unsigned int ientry=0; ientry<c_sig_only->GetEntries(); ++ientry){

   c_sig_only->GetEntry(ientry);

   for (unsigned int itrk=0; itrk<pt_reco->size(); ++itrk){

      //Cuts are applied

      if (reco_Chi2OverNDF->at(itrk)>5) continue;
      if (reco_Nhits->at(itrk)<6) continue;

      //Histograms are filled 

      if(abs(trueID->at(itrk))==13) {
        h_pt_reso_sig_only->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>0.0 && pt_reco->at(itrk)<2.5) h_pt_reso_sig_only_pt_00_25->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>2.5 && pt_reco->at(itrk)<5.0) h_pt_reso_sig_only_pt_25_50->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>5.0 && pt_reco->at(itrk)<7.5) h_pt_reso_sig_only_pt_50_75->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        if (pt_reco->at(itrk)>7.5 && pt_reco->at(itrk)<10.) h_pt_reso_sig_only_pt_75_100->Fill((pt_reco->at(itrk)-pt_true->at(itrk))/pt_true->at(itrk));
        }

      }
    }

  //Resolution as a function of pT

  TF1* f_gauss = new TF1("gauss","gaus(0)",-0.05,0.05);

  Double_t reso_sig_and_BIB[4];
  Double_t reso_sig_and_BIB_err[4];

  //Fit a gaussian for each pt bin

  h_pt_reso_sig_and_BIB_pt_00_25->Fit(f_gauss);
  reso_sig_and_BIB[0]=f_gauss->GetParameter(2)*100;
  reso_sig_and_BIB_err[0]=f_gauss->GetParError(2)*100;

  h_pt_reso_sig_and_BIB_pt_25_50->Fit(f_gauss);
  reso_sig_and_BIB[1]=f_gauss->GetParameter(2)*100;
  reso_sig_and_BIB_err[1]=f_gauss->GetParError(2)*100;

  h_pt_reso_sig_and_BIB_pt_50_75->Fit(f_gauss);
  reso_sig_and_BIB[2]=f_gauss->GetParameter(2)*100;
  reso_sig_and_BIB_err[2]=f_gauss->GetParError(2)*100;

  h_pt_reso_sig_and_BIB_pt_75_100->Fit(f_gauss);
  reso_sig_and_BIB[3]=f_gauss->GetParameter(2)*100;
  reso_sig_and_BIB_err[3]=f_gauss->GetParError(2)*100;

  Double_t reso_sig_only[4];
  Double_t reso_sig_only_err[4];

  h_pt_reso_sig_only_pt_00_25->Fit(f_gauss);
  reso_sig_only[0]=f_gauss->GetParameter(2)*100;
  reso_sig_only_err[0]=f_gauss->GetParError(2)*100;

  h_pt_reso_sig_only_pt_25_50->Fit(f_gauss);
  reso_sig_only[1]=f_gauss->GetParameter(2)*100;
  reso_sig_only_err[1]=f_gauss->GetParError(2)*100;

  h_pt_reso_sig_only_pt_50_75->Fit(f_gauss);
  reso_sig_only[2]=f_gauss->GetParameter(2)*100;
  reso_sig_only_err[2]=f_gauss->GetParError(2)*100;

  h_pt_reso_sig_only_pt_75_100->Fit(f_gauss);
  reso_sig_only[3]=f_gauss->GetParameter(2)*100;
  reso_sig_only_err[3]=f_gauss->GetParError(2)*100;

  //Graphs with resolution vs pt are obtained
 
  Double_t pt[4]={1.25,3.75,6.25,8.75};
  Double_t pt_err[4]={1.25,1.25,1.25,1.25};

  TGraphErrors* gr_reso_sig_and_BIB = new TGraphErrors(4,pt,reso_sig_and_BIB,pt_err,reso_sig_and_BIB_err);
  gr_reso_sig_and_BIB->SetMarkerColor(kRed);
  gr_reso_sig_and_BIB->SetLineColor(kRed);
  TGraphErrors* gr_reso_sig_only = new TGraphErrors(4,pt,reso_sig_only,pt_err,reso_sig_only_err);

  TCanvas* can_reso_vs_pt = new TCanvas("can_reso_vs_pt","can_reso_vs_pt",900,600);
  TMultiGraph *mg = new TMultiGraph();

  mg->Add(gr_reso_sig_and_BIB);
  mg->Add(gr_reso_sig_only);
  mg->GetXaxis()->SetTitle("p_{T} [GeV]");
  mg->GetYaxis()->SetTitle("track p_{T} resolution [%]");
  mg->Draw("ap");

  auto legend_gr = new TLegend(0.4,0.7,0.74,0.9);
  legend_gr->AddEntry(gr_reso_sig_only,"prompt muons","lep");
  legend_gr->AddEntry(gr_reso_sig_and_BIB,"prompt muons + BIB","lep");
  legend_gr->Draw();

  //Histograms for signal+BIB and signal only are plotted and compared

  TCanvas* can_pt_reso = new TCanvas("can_pt_reso","can_pt_reso",900,600);
  h_pt_reso_sig_only->Scale(1./h_pt_reso_sig_only->Integral());
  h_pt_reso_sig_only->Draw("histo");
  h_pt_reso_sig_and_BIB->SetLineColor(kRed);
  h_pt_reso_sig_and_BIB->Scale(1./h_pt_reso_sig_and_BIB->Integral());
  h_pt_reso_sig_and_BIB->Draw("histo same");
  
  auto legend = new TLegend(0.1,0.7,0.34,0.9);
  legend->AddEntry(h_pt_reso_sig_only,"prompt muons","l");
  legend->AddEntry(h_pt_reso_sig_and_BIB,"prompt muons + BIB","l");
  legend->Draw();
  
  return;
  }
