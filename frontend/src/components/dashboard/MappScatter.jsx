import { useMemo } from 'react'
import Plot from 'react-plotly.js'
import { useAnalysis } from '../../hooks/useAnalysis'
import { KARASEK_THRESHOLDS } from '../../utils/constants'
import { COLORS } from '../../utils/colors'

export default function MappScatter({ data }) {
  const { state } = useAnalysis()
  
  const plotData = useMemo(() => {
    if (!data?.rows) return []
    
    const rows = data.rows
    const quadCol = rows[0]?.Karasek_quadrant_theoretical ? 'Karasek_quadrant_theoretical' : 'Karasek_quadrant'
    
    if (!rows[0]?.Dem_score || !rows[0]?.Lat_score || !rows[0]?.[quadCol]) {
      return []
    }
    
    // Préparer les traces par quadrant
    const traces = {}
    
    rows.forEach(row => {
      const quad = row[quadCol]
      if (!traces[quad]) {
        traces[quad] = {
          x: [],
          y: [],
          text: [],
          name: quad,
          mode: 'markers',
          marker: {
            size: 7,
            opacity: 0.75,
            line: { width: 1, color: 'white' },
          },
        }
      }
      traces[quad].x.push(row.Lat_score)
      traces[quad].y.push(row.Dem_score)
      traces[quad].text.push(`${quad}`)
    })
    
    // Appliquer les couleurs
    return Object.entries(traces).map(([quad, trace]) => ({
      ...trace,
      marker: {
        ...trace.marker,
        color: COLORS.karasek[quad] || COLORS.muted,
      },
      hovertemplate: '<b>%{text}</b><br>Autonomie: %{x:.1f}<br>Charge: %{y:.1f}<extra></extra>',
    }))
  }, [data])

  const layout = useMemo(() => {
    const demThreshold = KARASEK_THRESHOLDS.Dem_score
    const latThreshold = KARASEK_THRESHOLDS.Lat_score
    
    return {
      plot_bgcolor: '#fafcff',
      paper_bgcolor: 'rgba(0,0,0,0)',
      font: { family: 'Plus Jakarta Sans, sans-serif', color: '#0f2340', size: 11 },
      title: {
        text: 'Demande Psychologique × Latitude Décisionnelle',
        font: { family: 'Fraunces, serif', size: 14, color: '#0f2340' },
        x: 0.02,
      },
      xaxis: {
        title: 'Latitude décisionnelle (autonomie & compétences)',
        titlefont: { size: 11, color: '#6b88a8' },
        tickfont: { size: 10, color: '#6b88a8' },
        gridcolor: '#edf5fd',
        zeroline: false,
        showline: true,
        linecolor: '#d6e8f7',
      },
      yaxis: {
        title: 'Demande psychologique (charge mentale)',
        titlefont: { size: 11, color: '#6b88a8' },
        tickfont: { size: 10, color: '#6b88a8' },
        gridcolor: '#edf5fd',
        zeroline: false,
      },
      legend: {
        bgcolor: 'rgba(255,255,255,0.95)',
        bordercolor: '#d6e8f7',
        borderwidth: 1,
        font: { size: 10, color: '#0f2340' },
        x: 0.98,
        y: 0.98,
        xanchor: 'right',
        yanchor: 'top',
      },
      hovermode: 'closest',
      margin: { l: 50, r: 20, t: 50, b: 50 },
      height: 450,
      
      // Lignes de seuil
      shapes: [
        // Quadrant Actif (haut-droite)
        {
          type: 'rect',
          x0: latThreshold, x1: 'max',
          y0: demThreshold, y1: 'max',
          fillcolor: COLORS.karasek.actif,
          opacity: 0.06,
          layer: 'below',
          line: { width: 0 },
        },
        // Quadrant Détendu (haut-gauche)
        {
          type: 'rect',
          x0: 'min', x1: latThreshold,
          y0: demThreshold, y1: 'max',
          fillcolor: COLORS.karasek.detendu,
          opacity: 0.06,
          layer: 'below',
          line: { width: 0 },
        },
        // Quadrant Tendu (bas-droite)
        {
          type: 'rect',
          x0: latThreshold, x1: 'max',
          y0: 'min', y1: demThreshold,
          fillcolor: COLORS.karasek.tendu,
          opacity: 0.06,
          layer: 'below',
          line: { width: 0 },
        },
        // Quadrant Passif (bas-gauche)
        {
          type: 'rect',
          x0: 'min', x1: latThreshold,
          y0: 'min', y1: demThreshold,
          fillcolor: COLORS.karasek.passif,
          opacity: 0.06,
          layer: 'below',
          line: { width: 0 },
        },
        // Ligne verticale (seuil Latitude)
        {
          type: 'line',
          x0: latThreshold, x1: latThreshold,
          y0: 'min', y1: 'max',
          line: { color: 'rgba(249, 115, 22, 0.45)', width: 1.5, dash: 'dot' },
        },
        // Ligne horizontale (seuil Demande)
        {
          type: 'line',
          x0: 'min', x1: 'max',
          y0: demThreshold, y1: demThreshold,
          line: { color: 'rgba(249, 115, 22, 0.45)', width: 1.5, dash: 'dot' },
        },
      ],
      
      // Annotations des quadrants
      annotations: [
        {
          xref: 'paper', yref: 'paper',
          x: 0.95, y: 0.95,
          text: 'ACTIF',
          showarrow: false,
          font: { size: 11, color: COLORS.karasek.actif, family: 'Plus Jakarta Sans' },
          xanchor: 'right', yanchor: 'top',
          opacity: 0.4,
        },
        {
          xref: 'paper', yref: 'paper',
          x: 0.05, y: 0.95,
          text: 'DÉTENDU',
          showarrow: false,
          font: { size: 11, color: COLORS.karasek.detendu, family: 'Plus Jakarta Sans' },
          xanchor: 'left', yanchor: 'top',
          opacity: 0.4,
        },
        {
          xref: 'paper', yref: 'paper',
          x: 0.95, y: 0.05,
          text: 'TENDU',
          showarrow: false,
          font: { size: 11, color: COLORS.karasek.tendu, family: 'Plus Jakarta Sans' },
          xanchor: 'right', yanchor: 'bottom',
          opacity: 0.4,
        },
        {
          xref: 'paper', yref: 'paper',
          x: 0.05, y: 0.05,
          text: 'PASSIF',
          showarrow: false,
          font: { size: 11, color: COLORS.karasek.passif, family: 'Plus Jakarta Sans' },
          xanchor: 'left', yanchor: 'bottom',
          opacity: 0.4,
        },
      ],
    }
  }, [])

  if (!plotData.length) {
    return (
      <div className="card flex items-center justify-center h-[450px]">
        <p className="text-muted">Données insuffisantes pour afficher la grille MAPP</p>
      </div>
    )
  }

  return (
    <div className="card">
      <Plot
        data={plotData}
        layout={layout}
        config={{
          displayModeBar: false,
          responsive: true,
          scrollZoom: false,
        }}
        useResizeHandler={true}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  )
}