from individual_systems import solve_individual_systems as sis
if __name__ == '__main__':
    sis(999)

# from modules.topology import create_microstructure_plurigaussian as cmp
# from modules import topology as tpl
# from modules.topology import add_roughness_all_phases as arap
# from modules.topology import downscale_domain as dd
# import numpy as np

# domain = tpl.create_circle(500,'quarter')
# interface_smooth = tpl.measure_interface(domain)
# dx = 12.5e-9
# domain1 = cmp(
#     voxels = [400,400], 
#     vol_frac = [0.4,0.3,0.3], 
#     d_ave = 250e-9, 
#     dx = dx, 
#     seed = [10,20], 
#     gradient_factor=1,
#     display = False,)

# domain2 = dd(domain1, 2)
# domain4 = dd(domain1, 4)
# domain8 = dd(domain1, 8)
# domain16 = dd(domain1, 16)



# D_rough = 30e-9
# rough_1 = arap(domain, iteration=4, d_rough=int(D_rough/dx))
# diff_1 = np.copy(rough_1)
# diff_1[domain!=rough_1] = 3

# rough_2 = tpl.add_roughness_all_phases(domain, iteration=2, d_rough=D)
# diff_2 = np.copy(rough_2)
# diff_2[rough_1!=rough_2] = 3

# rough_3 = tpl.add_roughness_all_phases(domain, iteration=3, d_rough=D)
# diff_3 = np.copy(rough_3)
# diff_3[rough_2!=rough_3] = 3

# surf_smooth = tpl.measure_interface(domain)
# surf_rough1 = tpl.measure_interface(rough_1)
# surf_rough2 = tpl.measure_interface(rough_2)
# surf_rough3 = tpl.measure_interface(rough_3)

# print([np.sum(surf_smooth), np.sum(surf_rough1), np.sum(surf_rough2), np.sum(surf_rough3)])
# from modules.postprocess import plot_domain as pd
# pd([domain1, domain2, domain4, domain8, domain16], qualitative=False, save=True)


# dx = 10e-9 
# R = 100e-9
# L = 2e-6
# overlap = 1.2
# freq = 2

# fibre = tpl.create_fibre(R,L)
# twisted_fibre = tpl.create_twisted_fibre(R,L,overlap=overlap,freq=freq, amp=amp)
# double_twisted_fibre = tpl.create_twisted_multifibre(int(R/dx),int(L/dx),overlap=overlap,freq=freq)
# rotated_fibre = tpl.rotate_3D_image(double_twisted_fibre, (10,20,40))
# bend_fibre = tpl.bend_fibre(double_twisted_fibre, 1.1)
# bed = tpl.create_fibrous_bed(
#         [200,100,100],
#         R, 
#         L, 
#         por,
#         freq = freq, 
#         overlap = 1, 
#         rotation_max = (0,90,90),
#         bend_max=1.1)
# bed, _, _ = tpl.percolation_analysis(bed)
# bend_fibre += 1
# _, _, lines, _ = tpl.measure_TPB(bend_fibre, dx)

# from modules.topology import create_microstructure_lattice as cml
# from modules.topology import measure_TPB as mtpb
# from modules.topology import create_microstructure_plurigaussian as cmp

# dx = 150e-9

# domain = cml(
#     [0.4,0.3,0.3], 
#     dx, 
#     [50,50,50], 
#     1e-6, 
#     offset=False, 
#     smallest_geometry=False)

# domain = cmp(
#     [500,100],
#     [0.4,0.3,0.3],
#     1e-6,
#     dx,
#     seed=[10,20],
#     mode='normal',
#     gradient_factor=8,
#     display=True,
# )

# _, _, vertices, lines = mtpb(bend_fibre, 10e-9)
# import pyvista as pv

# TPB_mesh = pv.PolyData(tpl.create_vertices_in_uniform_grid(bend_fibre.shape), lines=lines)

# from modules.postprocess import visualize_mesh as vm
# vm([bend_fibre],[(2,3)], TPB_mesh=TPB_mesh, clip_widget=True)
# vm([fibre,twisted_fibre,double_twisted_fibre,bend_fibre,bed], 
#    [(1,1),(1,1),(1,2),(1,2),(2,3)])