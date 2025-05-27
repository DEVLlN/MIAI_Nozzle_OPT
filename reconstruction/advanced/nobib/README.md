#Exercise on the signal+BIB overlay

#In this exercise you are going to learn how to overlay the beam-induced-background with a signal. You are going to learn how to check the reconstruction differences with and without the BIB.
#The chosen signal is an event with 1000 prompt muons, with uniform pt between 0 and 10 GeV. The signal has been already simulated for you, now you are going to reconstruct it.

#To reconstruct the signal without the BIB:

Marlin reco_sig_only_steer.xml > log_sig_only.log

#It will produce an histograms_sig_only.root output. 
#To reconstruct the signal overlayed with the BIB (10/2993 of the BIB bunch crossing is used as example):

Marlin reco_sig_and_BIB_steer.xml > log_sig_and_BIB.log

#It will produce an histograms_sig_and_BIB.root output. 
#Now we are going to compare the fitted track parameters in the two cases.
#A root file with a full signal+BIB reconstruction, a signal only reconstruction and a macro for the analysis has been prepared for you.

#In order to run the macro:

root -l
.L compare_sig_and_BIB.C
compare_sig_and_BIB()

#You can play with the cuts on the maximum chi2 (first argument) and on the number of hits (second argument) to clean your track sample. The third argument is used to chose the plot you want to see:
#0: chi2/ndof
#1: number of hits
#2: track pt
#3: D0 
#4: Z0 
#5: Omega 
#As example:  

root -l
.L compare_sig_and_BIB.C
compare_sig_and_BIB(5,6,3)

#In this way a maximum chi2/ndof of 5 and a minimum number of 6 hits is required, and the D0 comparison is shown.

#You can also measure the track pT resolution as a function of PT with the track_pt_resolution.C macro. You should simply type:

root -l
.L track_pt_resolution.C
track_pt_resolution()

#In this way you can compare the track pt resolution with and without the BIB.
