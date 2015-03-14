        data = {'position': (0.1,0.1,0.1), 'quaternion': (0.1,0.1,0.1,0.1)}
        
        dx, dy, dz = data['position']
        sideDim = 120
        Xsnap = False
        Ysnap = False
        Zsnap = False
        
        if max(dx, dy, dz) == dx:
            Xsnap = True
        elif max(dx, dy, dz) == dy:
            Ysnap = True
        else:
            Zsnap = True
            
        if Xsnap:
            cube.SetXLength(0)
            cube.SetYLength(sideDim)
            cube.SetZLength(sideDim)
        elif Ysnap:
            cube.SetXLength(sideDim)
            cube.SetYLength(0)
            cube.SetZLength(sideDim)
        elif Zsnap:
            cube.SetXLength(sideDim)
            cube.SetYLength(sideDim)
            cube.SetZLength(0)
