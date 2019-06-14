function A000_FF__ClickAndGo
%stub to  main processing sections of program.
tic
%BatchrunExpArray=[1];  %'VersionTest'; 
BatchrunExpArray=[2];  %see A000__FF_Get_JacobPathsandExperiments

for ii=1:length(BatchrunExpArray)
    batchrunindex=BatchrunExpArray(ii);
    if 1, A010_FF_GetGeneralImageProps(batchrunindex); end    
end
toc