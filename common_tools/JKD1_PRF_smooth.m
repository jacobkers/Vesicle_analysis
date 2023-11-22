function outdata=JKD1_PRF_smooth(data,span)
%running window 'span' smoothing average; 0=no smoothing.
%perioc boundaries
%JacobKers 2013

if span>0
    hs=ceil(span/2);
    le=length(data);
    outdata=zeros(le,1);
    midpt=ceil(le/2);
    data2=[data(midpt:end) ; data ; data(1:midpt)];
    lex=length(data(midpt:end));
    for i=1:le
    idx=i+lex;
    outdata(i)=mean(data2(idx-hs:idx+hs));
    end
else
    outdata=data; %no smoothing
end