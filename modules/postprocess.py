import numpy as np
def visualize_residuals(inputs, residuals):
    import pandas as pd
    import plotly.express as px

    # visualize the error
    x = np.arange(len(residuals[2]))
    r = [None]*3
    df = [None]*3
    titles = ['Hydrogen concentration', 'Electron potential', 'Ion potential']

    for p in [0,1,2]:
        if inputs['solver_options']['ion_only'] and p!=2:
            continue
        r[p] = np.stack((x, residuals[p]), axis=-1)
        df[p] = pd.DataFrame(r[p], columns=['iteration', 'residual'])
        df[p].insert(2, 'Variable', titles[p])

    df = pd.concat(df)
    fig = px.line(df, x='iteration', y='residual', color='Variable', log_y=True)
    fig.update_yaxes(exponentformat="e")
    fig.show()

def visualize_3D_matrix(inputs, dense_m, TPB_dict, plots):
    # visualize the solution

    img_flag = inputs['output_options']['img_output']
    csv_flag = inputs['output_options']['csv_output']
    plot1D_flag = inputs['output_options']['show_1D_plots']
    plot3D_flag = inputs['output_options']['show_3D_plots']

    if plot3D_flag:
        import pyvista as pv
        vertices = TPB_dict['vertices']
        lines = TPB_dict['lines']
        pv.set_plot_theme("document")
        TPB_mesh = pv.PolyData(vertices, lines=lines)
    
    dx = inputs['microstructure']['dx']
    mats = []
    thds = []
    log_scale = []
    titles = []

    dense_phi = dense_m['phi_dense']
    dense_cH2 = dense_m['cH2']
    dense_Vel = dense_m['Vel']
    dense_Vio = dense_m['Vio']
    dense_Ia = dense_m['Ia']
    dense_eta_act = dense_m['eta_act']
    dense_eta_con = dense_m['eta_con']
    
    N = dense_phi.shape

    x = np.arange(N[0])*dx*1e6

    if plots['cH2_1D'] and (plot1D_flag or csv_flag):
        cH2_avg = np.zeros(N[0])
        cH2_max = np.zeros(N[0])
        cH2_min = np.zeros(N[0])
        cH2_c_down = np.zeros(N[0])
        cH2_c_up = np.zeros(N[0])
        for i in range(N[0]):
            a = dense_cH2[i, :, :][~np.isnan(dense_cH2[i, :, :])]
            cH2_avg[i] = np.average(a)
            cH2_max[i] = np.max(a)
            cH2_min[i] = np.min(a)
            cH2_c_down[i], cH2_c_up[i] = mean_confidence_interval(a)
        if csv_flag: create_csv_output(x, cH2_avg, cH2_min, cH2_max, cH2_c_down, cH2_c_up, f'cH2_{inputs["file_options"]["id"]}')
        if plot1D_flag: plot_with_continuous_error(x, cH2_avg, cH2_c_down, cH2_c_up, x_title='Distance from anode (µm)', y_title='Hydrogen concentration (kg/m3)', title=f'cH2_{inputs["file_options"]["id"]}', save_img=img_flag)
    
    if plots['Vel_1D'] and (plot1D_flag or csv_flag):
        Vel_avg = np.zeros(N[0])
        Vel_max = np.zeros(N[0])
        Vel_min = np.zeros(N[0])
        Vel_c_down = np.zeros(N[0])
        Vel_c_up = np.zeros(N[0])
        for i in range(N[0]):
            a = dense_Vel[i, :, :][~np.isnan(dense_Vel[i, :, :])]
            Vel_avg[i] = np.average(a)
            Vel_max[i] = np.max(a)
            Vel_min[i] = np.min(a)
            Vel_c_down[i], Vel_c_up[i] = mean_confidence_interval(a)
        if csv_flag: create_csv_output(x, Vel_avg, Vel_min, Vel_max, Vel_c_down, Vel_c_up, f'Vel_{inputs["file_options"]["id"]}')
        if plot1D_flag: plot_with_continuous_error(x, Vel_avg, Vel_c_down, Vel_c_up, x_title='Distance from anode (µm)', y_title='Electron potential (V)', title=f'Vel_{inputs["file_options"]["id"]}', save_img=img_flag)

    if plots['Vio_1D'] and (plot1D_flag or csv_flag):
        Vio_avg = np.zeros(N[0])
        Vio_max = np.zeros(N[0])
        Vio_min = np.zeros(N[0])
        Vio_c_down = np.zeros(N[0])
        Vio_c_up = np.zeros(N[0]) 
        for i in range(N[0]):
            a = dense_Vio[i, :, :][~np.isnan(dense_Vio[i, :, :])]
            Vio_avg[i] = np.average(a)
            Vio_max[i] = np.max(a)
            Vio_min[i] = np.min(a)
            Vio_c_down[i], Vio_c_up[i] = mean_confidence_interval(a)
        if csv_flag: create_csv_output(x, Vio_avg, Vio_min, Vio_max, Vio_c_down, Vio_c_up, f'Vio_{inputs["file_options"]["id"]}')
        if plot1D_flag: plot_with_continuous_error(x, Vio_avg, Vio_min, Vio_max, Vio_c_down, Vio_c_up, x_title='Distance from anode (µm)', y_title='Ion potential (V)', title=f'Vio_{inputs["file_options"]["id"]}', save_img=img_flag)

    if True:
        Ia_A_avg = np.zeros(N[0])

        j_buch = 0         # area specific current density as defined in eq 21 by Buchaniec et al. 2019 [A/m2]
        j_prok = 0         # area specific current density as defined in eq 3.31 in Prokop's thesis 2020 [A/m2]

        area = N[1]*N[2]*dx**2 # [m2]
        for i in range(N[0]):
            if i == 0 or i == N[0]-1:
                Ia_A_avg[i] = np.nan
            else:
                a = dense_Ia[i, :, :][~np.isnan(dense_Ia[i, :, :])]     # [A/m3]

                j_buch = j_buch + (np.sum(a))*dx
                j_prok = j_prok + (np.sum(a))*dx**3
                
                Ia_A_avg[i] = j_prok/area # [A/m2]

        if csv_flag: create_csv_output(x, Ia_A_avg, title=f'Ia_A_{inputs["file_options"]["id"]}')
        if plot1D_flag: plot_with_continuous_error(x, Ia_A_avg, x_title='Distance from anode (µm)', y_title='Area-specific current density (A/m2)', title=f'Ia_A_{inputs["file_options"]["id"]}', save_img=img_flag)

    if inputs['output_options']['show_3D_plots']:
        if plots['cH2_3D'] and plot3D_flag:
            mats.append(dense_cH2)
            thds.append(())
            titles.append('cH2')
            log_scale.append(False)

        if plots['Vel_3D'] and plot3D_flag:
            mats.append(dense_Vel)
            thds.append(())
            titles.append('Vel')
            log_scale.append(False)
        
        if plots['Vio_3D'] and plot3D_flag:
            mats.append(dense_Vio)
            thds.append(())
            titles.append('Vio')
            log_scale.append(False)

        if plots['Ia_3D'] and plot3D_flag:
            mats.append(dense_Ia*dx**3)     # show the figure in [A] not [A/m3]
            thds.append(())
            titles.append('Ia')
            log_scale.append(True)

        if plots['eta_act_3D']and plot3D_flag:
            mats.append(dense_eta_act)
            thds.append(()) 
            titles.append('e_act')
            log_scale.append(False)

        if plots['eta_con_3D'] and plot3D_flag:
            mats.append(dense_eta_con)
            thds.append(())
            titles.append('e_con')
            log_scale.append(False)

        visualize_mesh(
            mat = mats,
            thd = thds,
            titles = titles,
            clip_widget = False, 
            TPB_mesh = TPB_mesh,
            log_scale = log_scale)
    
    return Ia_A_avg

def create_TPB_field_variable_individual(phi_dense, indices, masks_dict, func):
    # visualize a function on the TPB
    N = phi_dense.shape
    ds = masks_dict['ds']

    TPB_mat = np.zeros(shape = N)

    for p in [0,1,2]:
        for n in indices[p]['source']:
            i,j,k = indices[p]['all_points'][n]
            if close_to_edge(N, i,j,k): continue

            cH2_i = phi_dense[i,j,k] if p==0 else np.average(phi_dense[i-1:i+2,j-1:j+2,k-1:k+2][ds[0][i-1:i+2,j-1:j+2,k-1:k+2]])
            Vel_i = phi_dense[i,j,k] if p==1 else np.average(phi_dense[i-1:i+2,j-1:j+2,k-1:k+2][ds[1][i-1:i+2,j-1:j+2,k-1:k+2]])
            Vio_i = phi_dense[i,j,k] if p==2 else np.average(phi_dense[i-1:i+2,j-1:j+2,k-1:k+2][ds[2][i-1:i+2,j-1:j+2,k-1:k+2]])

            TPB_mat[i,j,k] = func(cH2_i, Vel_i, Vio_i)
    
    TPB_mat[TPB_mat==0] = np.nan
    return TPB_mat

def plot_with_continuous_error(x, y, y_min=None, y_max=None, y_c_down=None, y_c_up=None, 
                               x_title='x', y_title='y', title=None, save_img=False, log_type="linear"):
    import plotly.graph_objects as go

    x = [x] if type(x) is not list else x 
    y = [y] if type(y) is not list else y
    y_min = [y_min] if type(y_min) is not list else y_min
    y_max = [y_max] if type(y_max) is not list else y_max
    y_c_down = [y_c_down] if type(y_c_down) is not list else y_c_down
    y_c_up = [y_c_up] if type(y_c_up) is not list else y_c_up

    fig = go.Figure()
    for i in range(len(y)):
        if y_max[i] is not None:
            fig.add_trace(
                go.Scatter(
                    name='Upper Bound',
                    x=x[i],
                    y=y_max[i],
                    mode='lines',
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    showlegend=False,
                ))
            fig.add_trace(
                go.Scatter(
                    name='Lower Bound',
                    x=x[i],
                    y=y_min[i],
                    marker=dict(color="#444"),
                    line=dict(width=0),
                    mode='lines',
                    fillcolor='rgba(68, 68, 68, 0.3)',
                    fill='tonexty',
                    showlegend=False,
                ))

        # add y curve
        if y[i] is not None:
            fig.add_trace(go.Scatter(
                name='y',
                x=x[i],
                y=y[i],
                mode='lines',
                line=dict(color='rgb(31, 119, 180)'),
                showlegend=False,
            ))

        # add confidence level
        if y_c_down[i] is not None:
            fig.add_trace(go.Scatter(
                name='Continuous Lower Bound',
                x=x[i],
                y=y_c_down[i],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode='lines',
                # fillcolor='rgba(68, 68, 68, 0.7)',
                # fill='tonexty',
                showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                name='Continuous Upper Bound',
                x=x[i],
                y=y_c_up[i],
                marker=dict(color="#444"),
                line=dict(width=0),
                mode='lines',
                fillcolor='rgba(68, 68, 68, 0.7)',
                fill='tonexty',
                showlegend=False,
            ))


    fig.update_layout(
        yaxis_title=y_title,
        xaxis_title=x_title,
        title=title,
        hovermode=None,
    )

    fig.update_xaxes(exponentformat="SI") 
    fig.update_yaxes(exponentformat="e")
    fig.update_yaxes(type=log_type)
    fig.show()
    if save_img:
        dir = 'Binary files/1D plots/graphs/'
        create_directory(dir)
        file_dir = dir + f'{title if title is not None else "fig"}.html'
        fig.write_html(file_dir)

def mean_confidence_interval(data, confidence=0.95):
    import scipy.stats
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m-h, m+h

def create_field_variable_individual(N, phi, indices, func):
    field_mat = np.zeros(shape = N)

    for n in indices['interior']:
        i,j,k = indices['all_points'][n]
        field_mat[i,j,k] = func(phi[i,j,k])
    
    field_mat[field_mat==0] = np.nan
    return field_mat

def save_image(phase_mat):
    
    from tqdm import tqdm
    import imageio
    
    phase_1 = np.zeros(shape=phase_mat.shape)
    phase_1[phase_mat==1] = 1
    
    phase_2 = np.zeros(shape=phase_mat.shape)
    phase_2[phase_mat==2] = 2
    
    phase_3 = np.zeros(shape=phase_mat.shape)
    phase_3[phase_mat==3] = 3
    
    N = phase_mat.shape[0]
    for k in tqdm(np.arange(N)):
        str_1 = "images\phase_1."+f"{k:03}"
        imageio.imwrite(str_1, phase_1[:,:,k], format='png')     

def visualize_mesh(
        mat, 
        thd=[()], 
        blocks=[], 
        titles=[], 
        clip_widget=False, 
        TPB_mesh=[], 
        log_scale=None, 
        animation='none',
        save_graphics=None,
        elevation=0,
        azimuth=0,
        link_views=True):
    """
    Visualizes the mesh via PyVista.
    inputs:
    mat : float
        Three dimensional matrix describing the phase data. It could be list 
    """
    import pyvista as pv
    import matplotlib.pyplot as plt
    
    pv.set_plot_theme("document")
    cmap = plt.cm.get_cmap("viridis")
    
    zmin = min([np.nanmin(m) for m in mat])
    zmax = max([np.nanmax(m) for m in mat])
    clim = None
    
    subplts = len(mat)
    
    if bool(blocks): 
        p = pv.Plotter(shape=(1, subplts+1), border=True, notebook=False)
    else:
        p = pv.Plotter(shape=(1, subplts), border=True, notebook=False)
    
    for i in np.arange(subplts):
        scale = log_scale[i] if log_scale is not None else False
        sargs = dict(title=f'P{i+1}', height=0.15, vertical=True, position_x=0.01, position_y=0.8)
        sub_mat = mat[i]
        N=sub_mat.shape
        # Initializing grids
        mesh = pv.ImageData(dimensions=(N[0]+1,N[1]+1,N[2]+1))
        
        # Assigning values to grids
        mesh.cell_data["data"] = sub_mat.T.flatten()
        
        sub_thd = thd[i]
        if len(sub_thd)==0:
            mesh = mesh.threshold()
        if len(sub_thd)>0:
            mesh = mesh.threshold(sub_thd)
            
        p.subplot(0, i)
        # mesh.save(f"mesh{i}.vtk")
        if clip_widget:
            p.add_mesh_clip_plane(mesh, scalar_bar_args={'title': f'Phase{i+1}'}, cmap=cmap, clim=clim)
        else:
            p.add_mesh(mesh, scalar_bar_args=sargs, log_scale=scale, cmap=cmap, clim=clim)#, show_edges=True)
            p.add_bounding_box(line_width=1, color='black')
            if bool(titles):
                p.add_text(titles[i], font_size=20, position='lower_edge')
        if bool(TPB_mesh):
            p.add_mesh(TPB_mesh[i], line_width=10, color='r')
        
        p.view_isometric()
        p.camera_position = 'xy'
        # p.camera.clipping_range = (1e-2, 1e3)
        p.camera.elevation = elevation
        p.camera.azimuth = azimuth
        # p.show_grid()
        # p.remove_scalar_bar()
        # p.enable_parallel_projection()


    if bool(blocks):
        p.subplot(0, subplts)
        p.add_mesh(blocks)
        
    if link_views:
        p.link_views()

    if animation != 'none':
        p.open_movie("Binary files/animation.mp4")
        p.camera_position = 'xz'
        if animation == 'zoom':
            frames = 200
            final_zoom = 0.6
            initial_zoom = 0.1
            p.camera.zoom(initial_zoom)
            p.camera.clipping_range = (1e-2, 1e3)
            for value in np.linspace(0, 1, int(frames)):
                x = (final_zoom / initial_zoom)**(1/(frames))
                p.camera.zoom(x)
                p.camera.azimuth = value * 40
                p.camera.elevation = value * 20
                p.write_frame()
            frames = 400
            for value in np.linspace(0, 1, int(frames)):
                p.camera.azimuth = value * 360 + 40
                p.write_frame()
            p.close()
        elif animation == 'rotate':
            frames = 200
            p.camera.elevation = 20
            p.camera.zoom(1)
            for value in np.linspace(0, 1, int(frames)):
                p.camera.azimuth = value * 360
                p.write_frame()
            p.close()
    elif animation == 'none':
        if save_graphics is not None:
            file_name = 'img.' + save_graphics
            if save_graphics=='pdf' or save_graphics=='svg':
                p.save_graphic(file_name, raster=False, painter=False)
            elif save_graphics=='html':
                p.export_html("img.html")
        # pv.set_jupyter_backend('trame')
        p.show()
    return None
    
def visualize_network(volumes, centroids, M=1):
    import pyvista as pv
    
    blocks = pv.MultiBlock()
    
    for i in np.arange(len(volumes[M-1])):
        radius = np.power(volumes[M-1][i,:]*3/4/np.pi,1/3)
        center = np.flip(centroids[M-1][i,:])
        blocks.append(pv.Sphere(radius = radius, center = center))
                      
    return blocks

def visualize_contour(mat, n_levels=5):
    import pyvista as pv
    import matplotlib.pyplot as plt

    pv.set_plot_theme("document")
    cmap = plt.cm.get_cmap("jet")

    N=mat.shape[0]

    # Initializing grids
    mesh = pv.ImageData(dimensions=(N+1,N+1,N+1))
    mesh.cell_data["data"] = mat.flatten()
    mesh = mesh.threshold()
    mesh = mesh.cell_data_to_point_data()

    p = pv.Plotter(notebook=False)
    contours = mesh.contour(np.linspace(np.nanmin(mat), np.nanmax(mat), n_levels))    
    p.add_mesh(contours, cmap=cmap)

    # show the solid phase [needs improvement]
    # solid = np.zeros_like(mat)
    # solid[np.isnan(mat)] = 1
    # solid[~np.isnan(mat)] = np.nan
    # mesh_s = pv.ImageData(dimensions=(N+1,N+1,N+1))
    # mesh_s.cell_data["data"] = solid.flatten()
    # mesh_s = mesh_s.threshold()
    # cmap = plt.cm.get_cmap("Greys")
    # p.add_mesh(mesh_s, cmap=cmap,opacity=0.5)

    p.show()
    
    return None

def close_to_edge(N, i,j,k):
    if \
    (i==1 and j==1) or\
    (i==1 and k==1) or\
    (j==1 and k==1) or\
    (i==N[0]-2 and j==1) or\
    (i==N[0]-2 and k==1) or\
    (j==N[1]-2 and k==1) or\
    (i==1 and j==N[1]-2) or\
    (i==1 and k==N[2]-2) or\
    (j==1 and k==N[2]-2) or\
    (i==N[0]-2 and j==N[1]-2) or\
    (i==N[0]-2 and k==N[2]-2) or\
    (j==N[1]-2 and k==N[2]-2):
        return True

# specific functions for entire cell
def visualize_3D_matrix_entire_cell(inputs, phi_dense, masks_dict, TPB_dict, titles, cH2=None, Vel_a=None, Vio=None, cO2=None, Vel_c=None, field_mat=None, TPB_mat=None):
    # visualize the solution
    import pyvista as pv
    import pandas as pd
    import plotly.express as px
    pv.set_plot_theme("document")

    N = [inputs['Nx_a']+inputs['Nx_e']+inputs['Nx_c'], inputs['Ny'], inputs['Nz']]
    ds = masks_dict['ds']
    ds_entire_cell = [None]*5
    ds_entire_cell[0] = np.concatenate((ds[0], np.zeros((inputs['Nx_e']+inputs['Nx_c'], inputs['Ny'], inputs['Nz']),dtype=bool)), axis=0)
    ds_entire_cell[1] = np.concatenate((ds[1], np.zeros((inputs['Nx_e']+inputs['Nx_c'], inputs['Ny'], inputs['Nz']),dtype=bool)), axis=0)
    ds_entire_cell[2] = ds[2]
    ds_entire_cell[3] = np.concatenate((np.zeros((inputs['Nx_a']+inputs['Nx_e'], inputs['Ny'], inputs['Nz']),dtype=bool),ds[3]),axis=0)
    ds_entire_cell[4] = np.concatenate((np.zeros((inputs['Nx_a']+inputs['Nx_e'], inputs['Ny'], inputs['Nz']),dtype=bool),ds[4]),axis=0)
    mats = []
    thds = []
    log_scale = []
    
    if Vio is not None:
        sol_Vio = np.copy(phi_dense)
        sol_Vio[ds_entire_cell[2] == False] = np.nan
        mats.append(sol_Vio)
        thds.append(())
        log_scale.append(False)

    import pyvista as pv
    vertices_a = TPB_dict['anode']['vertices']
    lines_a = TPB_dict['anode']['lines']

    vertices_c = TPB_dict['cathode']['vertices']
    lines_c = TPB_dict['cathode']['lines']

    TPB_mesh_a = pv.PolyData(vertices_a, lines=lines_a)
    TPB_mesh_c = pv.PolyData(vertices_c, lines=lines_c)
    
    
    if inputs['show_3D_plots']:
        visualize_mesh(
            mat = mats,
            thd = thds,
            titles = titles,
            clip_widget = False, 
            TPB_mesh = [TPB_mesh_a, TPB_mesh_c],
            log_scale = log_scale)

    if inputs['show_1D_plots']:
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        Nx = inputs['Nx_a'] + inputs['Nx_e'] + inputs['Nx_c']
        x = np.arange(Nx)*inputs['dx']*1e6

        Vio_lin = np.zeros(Nx)
        Vio_min = np.zeros_like(Vio_lin)
        Vio_max = np.zeros_like(Vio_lin)
        Vio_c_up = np.zeros_like(Vio_lin)
        Vio_c_down = np.zeros_like(Vio_lin)

        for i in range(Nx):
            a = sol_Vio[i, :, :][~np.isnan(sol_Vio[i, :, :])]
            Vio_lin[i] = np.average(a)
            Vio_max[i] = np.max(a)
            Vio_min[i] = np.min(a)
            Vio_c_down[i], Vio_c_up[i] = mean_confidence_interval(a)

        plot_with_continuous_error(x, Vio_lin, Vio_max, Vio_min, Vio_c_down, Vio_c_up, x_title='Distance from anode (µm)', y_title='Hydrogen concentration (kg/m3)', title='Hydrogen concentration (kgm-3)')

def create_dense_matrices(inputs, phi, masks_dict, indices, field_functions, TPB_dict):
    write_arrays = inputs['output_options']['write_arrays']
    ds = masks_dict['ds']
    N = ds[0].shape
    phi_dense = np.zeros(N)
    phi_dense[ds[0]] = phi[0]
    phi_dense[ds[1]] = phi[1]
    phi_dense[ds[2]] = phi[2]
    Ia_mat = create_TPB_field_variable_individual(phi_dense, indices, masks_dict, field_functions['Ia'])
    eta_act_mat = create_TPB_field_variable_individual(phi_dense, indices, masks_dict, field_functions['eta_act'])
    eta_conc_mat = create_field_variable_individual(N, phi_dense, indices[0], field_functions['eta_con'])
    sol_cH2 = np.copy(phi_dense)
    sol_cH2[ds[0] == False] = np.nan
    sol_Vel = np.copy(phi_dense)
    sol_Vel[ds[1] == False] = np.nan
    sol_Vio = np.copy(phi_dense)
    sol_Vio[ds[2] == False] = np.nan

    if write_arrays:
        np.savez(f'Binary files/arrays/matrices_{inputs["file_options"]["id"]}.npz', 
                 phi=phi_dense, 
                 cH2=sol_cH2, 
                 Vel=sol_Vel, 
                 Vio=sol_Vio, 
                 Ia=Ia_mat, 
                 eta_act=eta_act_mat, 
                 eta_con=eta_conc_mat,
                 lines=TPB_dict['lines'])

    dense_m = {
        'phi_dense': phi_dense,
        'cH2': sol_cH2, 
        'Vel': sol_Vel, 
        'Vio': sol_Vio, 
        'Ia': Ia_mat, 
        'eta_act': eta_act_mat, 
        'eta_con': eta_conc_mat
        }
    return dense_m

def create_csv_output(x, y_avg, y_min=None, y_max=None, y_c_down=None, y_c_up=None, title='y'):
    import pandas as pd
    import os

    avg_title = title + '_avg'
    min_title = title + '_min'
    max_title = title + '_max'
    c_down_title = title + '_c_down'
    c_up_title = title + '_c_up'

    df = pd.DataFrame({'x': x, 
                       avg_title: y_avg, 
                       min_title: y_min, 
                       max_title: y_max, 
                       c_down_title: y_c_down, 
                       c_up_title: y_c_up})
    
    dir = 'Binary files/1D plots/csv/'
    create_directory(dir)
    df.to_csv(dir + title + '.csv', index=False)

def create_directory(dir):
    import os
    if not os.path.exists(dir):
        os.makedirs(dir)

def plot_domain(domains, gap=0, qualitative=True, save=False):
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.io as pio
    pio.renderers.default = "browser"

    # number of domains
    N = len(domains)

    # range of colorscale
    zmin = min([np.nanmin(d) for d in domains]).astype(int)
    zmax = max([np.nanmax(d) for d in domains]).astype(int)

    # choose a qualitiative colormap from zmin to zmax
    if qualitative:
        if zmin == zmax:
            colorscale = px.colors.qualitative.G10
        else:
            colorscale = [px.colors.qualitative.G10[i] for i in np.arange(zmax-zmin+1)]
    else:
        colorscale = 'Viridis'
        
    # create figure
    fig = make_subplots(rows=1, cols=N, )
    for n in range(N):
        fig.append_trace(go.Heatmap(z=domains[n], xgap=gap, ygap=gap, zmin=zmin, zmax=zmax, colorscale=colorscale, showscale=False), row=1, col=n+1)
        # scaleanchor = "x" if shared_axis else f"x{n+1}"
        fig.update_yaxes(
            scaleanchor=f"x{n+1}",
            scaleratio=1,
            row=1, col=n+1
            )
        # scaleanchor = "y" if shared_axis else f"y{n+1}"
        # fig.update_xaxes(
        #     scaleanchor=scaleanchor,
        #     scaleratio=1,
        #     row=1, col=n+1
        #     )
    
    fig.show()
    if save:
        fig.write_image("fig1.svg")

    