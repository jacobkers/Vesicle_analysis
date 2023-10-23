function [X,Y]=xy_unitlength_contour(X,Y,reps)
    for cc=1:reps
        %measure contour length; determine average distance between points
        CL=round(sum(((X(2:end)-X(1:end-1)).^2+...
                (Y(2:end)-Y(1:end-1)).^2).^0.5));  %approximate contour length
        unitlength=(mean(((X(2:end)-X(1:end-1)).^2+...
                (Y(2:end)-Y(1:end-1)).^2).^0.5))  %approximate unit step length
        [X,Y]=get_smooth_xyline(X,Y,CL);
    end
