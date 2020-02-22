import mplcursors
import numpy as np


def invertimage(img):
    img[:, :, :3] = 1 - img[:, :, :3]
    return img

def verticalplot(obj):
    angle = int(obj.directionbox.get())
    level = obj.evallevel

    if obj.verplotax is not None:
        obj.verplotax.cla()

    obj.verplotax.set_title(
        'Vertical plot exposure level vs distance at direction: {}° (level: {}m)'.format(angle, level))
    obj.verplotax.set_xlabel('Distance (m)')
    obj.verplotax.set_ylabel('Exposure level')

    xvalues, linedepps, xinterp, yinterp = obj.verticalvalues(angle, level)

    realplot = obj.verplotax.scatter(xvalues, linedepps, marker='.', color='blue')
    setver = obj.verplotax.scatter(xinterp, yinterp, alpha=0)

    interplot, = obj.verplotax.plot(xinterp, yinterp)

    interplot.set_label('Interpolated values')
    realplot.set_label('Sampled points/1°')
    obj.verplotax.set_xlim(0, obj.maxdistance)

    obj.verplotax.legend(loc=0, frameon=True, framealpha=0.8, facecolor='white')

    cursor = mplcursors.cursor(setver, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        i = sel.target.index
        sel.annotation.set_text(
            'd={0:04.2f}m \nExposure={1:4.2f}'.format(xinterp[i], yinterp[i]))

    obj.verplotax.fill_between(xinterp, 1, yinterp, where=yinterp > 1, facecolor='red', alpha=0.4)

    obj.verplotax.plot((0, xinterp[-1]), (1, 1), 'r--')

    if len(obj.x1markerbox.get()) == 0 or len(obj.x2markerbox.get()) == 0:
        obj.markersflag = False
    else:
        x1 = float(obj.x1markerbox.get())
        x2 = float(obj.x2markerbox.get())
        if (x1 >= x2) or (x1 < 0) or (x2 > obj.maxdistance):
            obj.markersflag = False
        else:
            obj.markersflag = True

    if obj.markersflag:
        x1idx = np.argmin(xinterp <= x1) - int(1)
        x2idx = np.argmax(xinterp >= x2)

        maxidx = np.argmax(np.where((xinterp >= xinterp[x1idx]) & (xinterp <= xinterp[x2idx]), yinterp, -1))

        obj.verplotax.stem([xinterp[x1idx], xinterp[x2idx]], [yinterp[x1idx], yinterp[x2idx]],
                            use_line_collection=True, basefmt=' ', linefmt='g--', markerfmt='go')
        obj.verplotax.fill_between(xinterp[x1idx:x2idx + 1], 0, yinterp[x1idx:x2idx + 1], facecolor='green',
                                    alpha=0.4)
    else:
        maxidx = np.argmax(yinterp)

    maxdepps = yinterp[maxidx]
    xmax = xinterp[maxidx]

    if xmax >= 0.5 * obj.maxdistance:
        xtext = xmax - 3
    else:
        xtext = xmax + 1.5

    ytext = maxdepps + 0.2
    if 0.9 < ytext < 1.1:
        ytext = ytext - 0.2

    globalmaxdepps = np.max(yinterp)

    obj.verplotax.set_ylim(0, max(globalmaxdepps + 0.1, ytext + 0.2, 1.1))

    text = 'Max:{:.2f}\nd={:.1f}m'.format(maxdepps, xmax)
    obj.verplotax.annotate(text, xy=(xmax, maxdepps), xycoords='data', xytext=(xtext, ytext), textcoords='data',
                            arrowprops=dict(facecolor='black', shrink=0.01, width=1, headwidth=3),
                            horizontalalignment='left', verticalalignment='center')

    # verann.remove()
    obj.lineplotscanvas.draw()
    # obj.verplotax.grid(color='white', alpha=1, linewidth=0.6)


def horizontalplot(obj):
    # horizontal safety plot:
    global phi1, phi2
    obj.horplotax.cla()

    obj.horplotax.set_title('Horizontal plot safety distance')
    #        obj.horplotax.set_xlabel('Angle (°)')
    #        obj.horplotax.set_ylabel('Rm (m)')
    #        obj.horplotax.set_xlim(-180, 180)
    #        obj.horplotax.xaxis.set_major_locator(ticker.MultipleLocator(30))

    rmvalues = np.zeros(361)
    phivalues = np.linspace(0, 360, 361).astype(int)

    for phi in phivalues:
        rmvalues[phi] = obj.horizontalsafety(phi)

    theta = np.linspace(0, 2 * np.pi, 361)
    sethor = obj.horplotax.scatter(theta, rmvalues, alpha=0)
    obj.horplotax.plot(theta, rmvalues)
    obj.horplotax.set_theta_zero_location("N")
    obj.horplotax.set_theta_direction(-1)

    obj.maxdistance = int(np.ceil(np.max(rmvalues)))
    obj.maxphi = int(np.argmax(rmvalues))
    if len(obj.directionbox.get()) == 0:
        obj.directionbox.insert(0, obj.maxphi)

    cursor = mplcursors.cursor(sethor, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        i = sel.target.index
        sel.annotation.set_text(
            'φ={0:0.0f}° \nRm={1:4.2f}m'.format(phivalues[i], rmvalues[i]))

    if len(obj.phi1markerbox.get()) == 0 or len(obj.phi2markerbox.get()) == 0:
        obj.phimarkersflag = False
    else:
        obj.phimarkersflag = True
        phi1 = int(obj.phi1markerbox.get())
        phi2 = int(obj.phi2markerbox.get())

        if phi1 < 0:
            phi1 += 360
        if phi2 < 0:
            phi2 += 360

        if phi1 > 360:
            phi1 -= 360
        if phi2 > 360:
            phi2 -= 360

    _, ymax = obj.horplotax.get_ylim()

    textvar1 = 'Max Rm: {:.1f}m \nat φ = {}°'.format(np.max(rmvalues), obj.maxphi)
    obj.horplotax.text(-0.7, 0.7, textvar1, transform=obj.horplotax.transAxes, fontsize=11)
    if obj.phimarkersflag:

        if phi1 < phi2:
            localrm = np.amax(np.where((phivalues >= phi1) & (phivalues <= phi2), rmvalues, -1))
            obj.horplotax.fill_between(np.linspace(np.deg2rad(phi1), np.deg2rad(phi2), phi2 - phi1 + 1), 0,
                                        rmvalues[phi1:phi2 + 1], alpha=0.3, color='g')
        else:
            obj.horplotax.fill_between(np.linspace(np.deg2rad(phi1), 2 * np.pi, 361 - phi1), 0, rmvalues[phi1:361],
                                        alpha=0.3, color='g')
            obj.horplotax.fill_between(np.linspace(0, np.deg2rad(phi2), phi2 + 1), 0, rmvalues[0:phi2 + 1],
                                        alpha=0.3, color='g')
            rm1 = np.amax(np.where((phivalues >= phi1), rmvalues, -1))
            rm2 = np.amax(np.where((phivalues <= phi1), rmvalues, -1))
            localrm = max(rm1, rm2)
        obj.horplotax.plot([np.deg2rad(phi1), np.deg2rad(phi1)], [0, ymax], color="green", linewidth=2)
        obj.horplotax.plot([np.deg2rad(phi2), np.deg2rad(phi2)], [0, ymax], color="green", linewidth=2)
        textvar2 = 'Safety distance from {}° to {}°:\n{:.1f}m'.format(phi1, phi2, localrm)
        obj.horplotax.text(-0.7, 0.9, textvar2, transform=obj.horplotax.transAxes, fontsize=11)
        
def contourplot(obj):
    obj.contourplotbtn.config(state='disabled', text='Progressing..')
    obj.reget_grid()

    obj.totaldeppsgrid()
    maxexposure = np.amax(obj.zvalues)
    # IMAGE PLOT

    obj.contourplotax.cla()

    if obj.cb is not None:
        obj.cb.remove()

    level = obj.evallevel

    obj.contourplotax.set_title('Maximum exposure at level h={}m: {:.3f}'.format(level, maxexposure))
    obj.contourplotax.set_xlabel('x (m)')
    obj.contourplotax.set_ylabel('y (m)')

    limits = [-obj.xlimit, obj.xlimit, -obj.ylimit, obj.ylimit]

    # plot custom zvalues on image, with custom transparency mask
    if len(obj.thresholdlevelbox.get()) == 0:
        obj.thresholdlevelbox.insert(0, 0.8)

    threshold = float(obj.thresholdlevelbox.get())

    customval = np.full_like(obj.zvalues, np.nan)
    mask = (obj.zvalues >= threshold)
    customval[mask] = obj.zvalues[mask]


    obj.contourplotax.imshow(obj.img, interpolation='bicubic', extent=limits)

    obj.contourplotax.grid(None)

    obj.bsmarker = obj.contourplotax.scatter(obj.bsxposition, obj.bsyposition, c='green', edgecolors='white')
    obj.bsmarkertext = obj.contourplotax.annotate('BS', (obj.bsxposition, obj.bsyposition),
                                                    xytext=(0.1 + obj.bsxposition, obj.bsyposition + 0.1),
                                                    c='white')

    if obj.lowlevelsplotvar.get() == 1:
        lowlevels = np.full_like(obj.zvalues, np.nan)
        lowlevels[~mask] = obj.zvalues[~mask]
        obj.contourplotax.imshow(lowlevels, interpolation='none', cmap='Greens',
                                  extent=limits, alpha=0.3)

    layer2 = obj.contourplotax.imshow(customval, interpolation='none', cmap='YlOrRd',
                                       extent=limits, alpha=0.7, vmin=threshold, vmax=1)

    tickvalues = np.linspace(threshold, 1, 5)
    ticklabels = []
    for val in tickvalues:
        ticklabels.append('{:.2f}'.format(val))

    ticklabels[-1] = ' >= 1'

    if maxexposure >= threshold:
        obj.cb = obj.contourplotfig.colorbar(layer2, ax=obj.contourplotax, ticks=tickvalues)
        ax = obj.contourplotax
        obj.cb.ax.set_yticklabels(ticklabels)

    cursor = mplcursors.cursor(layer2)
    obj.contourplotcanvas.draw()

    @cursor.connect("add")
    def on_add(sel):
        i, j = sel.target.index
        sel.annotation.set_text(
            'Exposure={0:04.2f} \nrho={1:0.1f}m \nφ={2:0.0f}°'.format(obj.zvalues[i, j], obj.rho2[i, j],
                                                                      obj.phi2[i, j]))

    obj.contourplotbtn.config(state='normal', text='Recalculate')