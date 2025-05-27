void compare_sig_and_BIB(Double_t chi2_max=20., Int_t nhits_min=0, Int_t plot_ID=0){

  cout << "Usage: " << endl;
  cout << "compare_sig_and_BIB(Double_t chi2_max=20., Int_t nhits_min=0, Int_t plot_ID=0)"<< endl;
  cout << "Plot IDs are the following" << endl;
  cout << "0: chi2/ndof" << endl;
  cout << "1: number of hits" << endl;
  cout << "2: track pt" << endl;
  cout << "3: D0" << endl;
  cout << "4: Z0" << endl;
  cout << "5: Omega" << endl;

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

  TH1F* h_reco_Chi2OverNDF_sig_and_BIB = new TH1F("h_reco_Chi2OverNDF_sig_and_BIB",";track #chi^{2}/ndof",120,-1,20);
  TH1F* h_recoNhits_sig_and_BIB = new TH1F("h_recoNhits_sig_and_BIB",";number of hits",20,0,20); 
  TH1F* h_recoPt_sig_and_BIB = new TH1F("h_recoPt_sig_and_BIB",";p_{T} [GeV]",40,0,10);
  TH1F* h_recoOmega_sig_and_BIB = new TH1F("h_recoOmega_sig_and_BIB",";#omega [1/mm]",200,-0.01,0.01);
  TH1F* h_recoD0_sig_and_BIB = new TH1F("h_recoD0_sig_and_BIB",";D0 [mm]",140,-0.5,0.5);
  TH1F* h_recoZ0_sig_and_BIB = new TH1F("h_recoZ0_sig_and_BIB",";Z0 [mm]",400,-2,2);

  TH1F* h_reco_Chi2OverNDF_sig_only = new TH1F("h_reco_Chi2OverNDF_sig_only",";track #chi^{2}/ndof",120,-1,20);
  TH1F* h_recoNhits_sig_only = new TH1F("h_recoNhits_sig_only",";number of hits",20,0,20);
  TH1F* h_recoPt_sig_only = new TH1F("h_recoPt_sig_only",";p_{T} [GeV]",40,0,10);
  TH1F* h_recoOmega_sig_only = new TH1F("h_recoOmega_sig_only",";#omega [1/mm]",200,-0.01,0.01);
  TH1F* h_recoD0_sig_only = new TH1F("h_recoD0_sig_only",";D0 [mm]",140,-0.5,0.5);
  TH1F* h_recoZ0_sig_only = new TH1F("h_recoZ0_sig_only",";Z0 [mm]",400,-2,2);

  //Count tracks

  Int_t ntracks_sig_and_BIB =0;
  Int_t ntracks_sig_only =0;

  //Loop on the events for signal+BIB

  for(unsigned int ientry=0; ientry<c_sig_and_BIB->GetEntries(); ++ientry){

   c_sig_and_BIB->GetEntry(ientry);

   //Loop on the tracks 

   for (unsigned int itrk=0; itrk<pt_reco->size(); ++itrk){

      //Cuts are applied

      if (reco_Chi2OverNDF->at(itrk)>chi2_max) continue;
      if (reco_Nhits->at(itrk)<nhits_min) continue;

      ntracks_sig_and_BIB++;

      //Histograms are filled

      h_reco_Chi2OverNDF_sig_and_BIB->Fill(reco_Chi2OverNDF->at(itrk));
      h_recoNhits_sig_and_BIB->Fill(reco_Nhits->at(itrk));
      h_recoPt_sig_and_BIB->Fill(pt_reco->at(itrk));
      h_recoD0_sig_and_BIB->Fill(d0_reco->at(itrk));
      h_recoZ0_sig_and_BIB->Fill(z0_reco->at(itrk));  
      if(trueID->at(itrk)<=0) h_recoOmega_sig_and_BIB->Fill((0.3*4.)/(pt_reco->at(itrk)*1000.));
      if(trueID->at(itrk)>0)  h_recoOmega_sig_and_BIB->Fill(-(0.3*4.)/(pt_reco->at(itrk)*1000.));

      }
    }

  //Loop on the events for signal only

  for(unsigned int ientry=0; ientry<c_sig_only->GetEntries(); ++ientry){

   c_sig_only->GetEntry(ientry);

   for (unsigned int itrk=0; itrk<pt_reco->size(); ++itrk){

      //Cuts are applied

      if (reco_Chi2OverNDF->at(itrk)>chi2_max) continue;
      if (reco_Nhits->at(itrk)<nhits_min) continue;

      ntracks_sig_only++;

      //Histograms are filled 

      h_reco_Chi2OverNDF_sig_only->Fill(reco_Chi2OverNDF->at(itrk));
      h_recoNhits_sig_only->Fill(reco_Nhits->at(itrk));
      h_recoPt_sig_only->Fill(pt_reco->at(itrk));
      h_recoD0_sig_only->Fill(d0_reco->at(itrk));
      h_recoZ0_sig_only->Fill(z0_reco->at(itrk)); 
      if(trueID->at(itrk)<=0) h_recoOmega_sig_only->Fill((0.3*4.)/(pt_reco->at(itrk)*1000.));
      if(trueID->at(itrk)>0)  h_recoOmega_sig_only->Fill(-(0.3*4.)/(pt_reco->at(itrk)*1000.));

      }
    }

  //Histograms for signal+BIB and signal only are plotted and compared

  h_reco_Chi2OverNDF_sig_and_BIB->SetLineColor(kRed);
  auto legend = new TLegend(0.4,0.7,0.74,0.9);
  legend->AddEntry(h_reco_Chi2OverNDF_sig_only,"prompt muons","l");
  legend->AddEntry(h_reco_Chi2OverNDF_sig_and_BIB,"prompt muons + BIB","l");

  if (plot_ID==0){

    TCanvas* can_Chi2OverNDF = new TCanvas("can_Chi2OverNDF","can_Chi2OverNDF",900,600);
    h_reco_Chi2OverNDF_sig_only->Scale(1./h_reco_Chi2OverNDF_sig_only->Integral());
    h_reco_Chi2OverNDF_sig_only->Draw("histo");
    h_reco_Chi2OverNDF_sig_and_BIB->SetLineColor(kRed);
    h_reco_Chi2OverNDF_sig_and_BIB->Scale(1./h_reco_Chi2OverNDF_sig_and_BIB->Integral());
    h_reco_Chi2OverNDF_sig_and_BIB->Draw("histo same"); 
    legend->Draw();
  
    }

  if (plot_ID==1){
    TCanvas* can_recoNhits = new TCanvas("can_recoNhits","can_recoNhits",900,600);
    h_recoNhits_sig_and_BIB->SetLineColor(kRed);
    h_recoNhits_sig_and_BIB->Scale(1./h_recoNhits_sig_and_BIB->Integral());
    h_recoNhits_sig_and_BIB->Draw("histo");
    h_recoNhits_sig_only->Scale(1./h_recoNhits_sig_only->Integral());
    h_recoNhits_sig_only->Draw("histo same");
    legend->Draw();
    }
  
  if (plot_ID==2){
    TCanvas* can_recoPt = new TCanvas("can_recoPt","can_recoPt",900,600);
    h_recoPt_sig_and_BIB->SetLineColor(kRed);
    h_recoPt_sig_and_BIB->Scale(1./h_recoPt_sig_and_BIB->Integral());
    h_recoPt_sig_and_BIB->Draw("histo");
    h_recoPt_sig_only->Scale(1./h_recoPt_sig_only->Integral());
    h_recoPt_sig_only->Draw("histo same");
    legend->Draw();
    }

  h_recoD0_sig_and_BIB->SetLineColor(kRed);
  auto legend2 = new TLegend(0.1,0.7,0.34,0.9);
  legend2->AddEntry(h_recoD0_sig_only,"prompt muons","l");
  legend2->AddEntry(h_recoD0_sig_and_BIB,"prompt muons + BIB","l");

  if (plot_ID==3){
    TCanvas* can_recoD0 = new TCanvas("can_recoD0","can_recoD0",900,600);
    h_recoD0_sig_only->Scale(1./h_recoD0_sig_only->Integral());
    h_recoD0_sig_only->Draw("histo");
    h_recoD0_sig_and_BIB->SetLineColor(kRed);
    h_recoD0_sig_and_BIB->Scale(1./h_recoD0_sig_and_BIB->Integral());
    h_recoD0_sig_and_BIB->Draw("histo same");
    legend2->Draw();
    }  

  if (plot_ID==4){
    TCanvas* can_recoZ0 = new TCanvas("can_recoZ0","can_recoZ0",900,600);
    h_recoZ0_sig_only->Scale(1./h_recoZ0_sig_only->Integral());
    h_recoZ0_sig_only->Draw("histo");
    h_recoZ0_sig_and_BIB->SetLineColor(kRed);
    h_recoZ0_sig_and_BIB->Scale(1./h_recoZ0_sig_and_BIB->Integral());
    h_recoZ0_sig_and_BIB->Draw("histo same");
    legend2->Draw();
    }

  if (plot_ID==5){
    TCanvas* can_recoOmega = new TCanvas("can_recoOmega","can_recoOmega",900,600);
    h_recoOmega_sig_only->Scale(1./h_recoOmega_sig_only->Integral());
    h_recoOmega_sig_only->Draw("histo");
    h_recoOmega_sig_and_BIB->SetLineColor(kRed);
    h_recoOmega_sig_and_BIB->Scale(1./h_recoOmega_sig_and_BIB->Integral());
    h_recoOmega_sig_and_BIB->Draw("histo same");
    legend2->Draw();
    }

  cout << "number of tracks with signal+BIB = " <<  ntracks_sig_and_BIB << endl;
  cout << "number of tracks with signal only = " <<  ntracks_sig_only << endl;
   
  return;
  }
