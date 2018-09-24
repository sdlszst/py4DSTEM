# Defines a class - DataCube - for storing / accessing / manipulating the 4D-STEM data
#
# Datacube objects can be generated by the reader() function, which accepts a filepath and outputs
# a Datacube.
# Datacube objects are saved as .h5 files. The writer() function accepts a Datacube, and spit out
# a .h5.
#
#
### A note on metadata ##
# Metadata exists in 3 different ways in the program.
# (1) At readtime, hyperspy reads in the file and stores metadata in the native hyperspy tree
# structure hyperspy.misc.utils.DictionaryTreeBrowser
# (2) Any metadata that is important to the py4DSTEM will be saved as an attribute in the 
# DataCube object.  The Datacube additionally keeps a copy of the original hyperspy metadata trees
# (3) When saved to a .h5, metadata is copied into a metadata group.  This includes, in separate
# subgroups, both the original hyperspy metadata (in an identical tree structure, written in .h5
# groups/attrs), and the metadata used by py4DSTEM


import hyperspy.api as hs
import numpy as np

class DataCube(object):

    def __init__(self, data, R_Ny, R_Nx, Q_Ny, Q_Nx, original_metadata_shortlist=None, original_metadata_all=None, filename=None):
        self.data4D = data
        self.R_Ny, self.R_Nx = R_Ny, R_Nx
        self.Q_Ny, self.Q_Nx = Q_Ny, Q_Nx
        self.R = R_Ny*R_Nx
        self.original_metadata_shortlist = original_metadata_shortlist
        self.original_metadata_all = original_metadata_all
        self.filename = filename

    def set_scan_shape(self,R_Ny,R_Nx):
        """
        Reshape the data give the real space scan shape.
        TODO: insert catch for 4D data being reshaped.  Presently only 3D data supported.
        """
        try:
            self.data4D = self.data4D.reshape(self.R_Ny*self.R_Nx,self.Q_Ny,self.Q_Nx).reshape(R_Ny,R_Nx,self.Q_Ny,self.Q_Nx)
            #self.data4D = self.self.data4D.reshape(R_Ny,R_Nx,self.Q_Ny,self.Q_Nx)
            self.R_Ny,self.R_Nx = R_Ny, R_Nx
        except ValueError:
            pass

    def get_diffraction_space_view(self,y=0,x=0):
        """
        Returns the image in diffraction space, and a Bool indicating success or failure.
        """
        self.x,self.y = x,y
        try:
            return self.data4D[y,x,:,:].T, 1
        except IndexError:
            return 0, 0

    def get_real_space_view(self,slice_y,slice_x):
        """
        Returns the image in diffraction space.
        """
        return self.data4D[:,:,slice_y,slice_x].sum(axis=(2,3)).T, 1

    def cropAndBin(self, bin_r, bin_q, crop_r, crop_q, slice_ry, slice_rx, slice_qy, slice_qx):
        # If binning is being performed, edit crop window as neededd

        # Crop data

        # Bin data
        self.bin_diffraction(bin_q)
        self.bin_real(bin_r)
        pass


    def bin_diffraction(self,bin_q):
        """
        Performs binning by a factor of bin_q on data4D.
        """
        if bin_q<=1:
            return
        else:
            assert type(bin_q) is int, "Error: binning factor {} is not an int.".format(bin_q)
            R_Ny,R_Nx,Q_Ny,Q_Nx = self.data4D.shape
            # Ensure array is well-shaped for binning
            if ((Q_Ny%bin_q == 0) and (Q_Nx%bin_q == 0)):
                pass
            else:
                self.data4D = self.data4D[:,:,:-(Q_Ny%bin_q),:-(Q_Nx%bin_q)]
            self.data4D = self.data4D.reshape(R_Ny,R_Nx,int(Q_Ny/bin_q),bin_q,int(Q_Nx/bin_q),bin_q).sum(axis=(3,5))
            return

    def bin_real(self,bin_r):
        """
        Performs binning by a factor of bin_r on data4D.
        """
        if bin_r<=1:
            return
        else:
            assert type(bin_r) is int, "Error: binning factor {} is not an int.".format(bin_r)
            R_Ny,R_Nx,Q_Ny,Q_Nx = self.data4D.shape
            # Ensure array is well-shaped for binning
            if ((R_Ny%bin_r == 0) and (R_Nx%bin_r == 0)):
                pass
            else:
                self.data4D = self.data4D[:-(R_Ny%bin_r),:-(R_Nx%bin_r),:,:]
            self.data4D = self.data4D.reshape(int(R_Ny/bin_r),bin_r,int(R_Nx/bin_r),bin_r,Q_Ny,Q_Nx).sum(axis=(1,3))
            return

