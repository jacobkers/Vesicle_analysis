import numpy as np
import xarray as xr

# GUV Image Analysis Pipeline
Guvs = xr.open_dataset("example.nc")
print(Guvs)


# 1. Take DataArray out
R0 = Guvs["R0"]

R_av = R0.mean(dim="index")
# 2. Add an attribute: a 1D processed value belonging to that property
# make a copy so you don’t mutate Guvs in-place
R0=R0.copy()
R0.attrs["mean"] = float(R_av.values)
Guvs["R0"].attrs["mean"] = float(R_av.values)

# 3. Put it back into the Dataset: either by adding the copy,
# or by only the # mean
#Guvs = Guvs.assign(R0=R0)
Guvs["R0"].attrs["mean"] = float(R_av.values)

Guvs.to_netcdf("..\example.nc", mode="w")

print(Guvs)
print('aaaanndd:')
print(Guvs["R0"].attrs["mean"])
