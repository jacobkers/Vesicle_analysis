function decay=Bleachcurvefit(yori);
%Fit an exponential decay

close all;
if nargin<1
    tau=100;
    ax = linspace(1,1000);
    yori = 7*(ax/tau).^2.*exp(-ax/tau);
end

xori=1:length(yori);

%1) precook
% subtract, normalize, find the tail;
ym=0;  %min(yori);
[val,idx]=max(yori-ym);
idx=round(1.2*idx);  %just beyond max
yt=(yori(idx:end)-ym)/val;
xt=xori(1:length(yt));


%2 start estimate; 
   lo_b=0;       lo_c=length(yt)/100; 
   st_b=0.7;       st_c=length(yt)/2;
   hi_b=2;         hi_c=5*length(yt);
%end

fo = fitoptions('Method','NonlinearLeastSquares',...
               'Lower',[lo_b lo_c],...
               'Upper',[hi_b hi_c],...
               'StartPoint',[st_b st_c]);
myfittype = fittype('b*exp(-x/c)',...
    'dependent',{'y'},'independent',{'x'},...
    'coefficients',{'b', 'c'},'options',fo);
myfit = fit(xt',yt',myfittype);
yfit=myfit.b*exp(-xt/myfit.c);




if nargin<1
    plot(xori,yori); hold on;    
    plot(xt+idx,val*yfit+ym,'r', 'LineWidth', 2);
    text(xt(1),0.5*max(yori),num2str(myfit.c));
    ylim([0 1.2*max(yori)]);
    legend('data','fit');
    [~]=ginput(1);
end
decay=myfit.c;
dum=1;