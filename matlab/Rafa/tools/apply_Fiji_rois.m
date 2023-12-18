function Iph_out=apply_Fiji_rois(Iph,pathinfo, FOV_specifier)
% Open Fiji/imageJ
% Open BF or Phase
% Select "round" ROI
% Find the position and press "T" to load it into the ROI manager (check "show all" box)
% Click into the ROI manager window and CTRL+A to select all ROIs
% CLick More>list>File>Save As> "Overlay Elements of 4595_SyG_001"
% This saves a excel file into the file location.
%columns: %Index	Name	Type	X	Y	Width	Height	Color	Fill	LWidth	Pos	C	Z	T
%need: X, Y, Width, Height(4-7)
msk=0*Iph;

[rr,cc]=size(Iph);
[XX,YY]=meshgrid(1:cc,1:rr);
% Overlay Elements of 4595_SyG_001
csv_source_for_all=[pathinfo.experimentpath, 'Overlay Elements.csv'];

csv_source_for_just_these=[pathinfo.experimentpath,'Overlay Elements of ', FOV_specifier, '.csv'];

if isfile(csv_source_for_all), csv_source=csv_source_for_all; end
if isfile(csv_source_for_just_these), csv_source=csv_source_for_just_these; end

if isfile(csv_source_for_all) | isfile(csv_source_for_just_these)
    roidata=readtable(csv_source);
    if ~isempty(roidata)
        disp('applying IMageJ-based masking');
        pos_xx=roidata.X+roidata.Width/2;  %corner point plus half-width
        pos_yy=roidata.Y+roidata.Height/2;  %analogous
        pos_rr=roidata.Width/2; % app.radius
        N_rois=length(pos_xx);
        for ii=1:N_rois
            xi=pos_xx(ii);
            yi=pos_yy(ii);
            ri=pos_rr(ii);
            RR=((XX-xi).^2+(YY-yi).^2).^0.5;
            sel=find(RR<ri);
            msk(sel)=1;
            dum=1;
        end
        Iph_out=msk.*Iph;
        Iph_out(Iph_out==0)=median(Iph(:));

        %demo plot
        if 0
            figure;
            dipshow(Iph); hold on;
            plot(pos_xx,pos_yy, 'rx');
            title('selected rois');
            figure;
            dipshow(Iph_out); hold on;
            title('masked');
            [~]=ginput(1);
        end
    else
        disp('working all image area');
        Iph_out=Iph;
    end
else
    disp('working all image area');
    Iph_out=Iph;
end
dum=1;
