import ReactECharts from 'echarts-for-react'
import LoadingSkeleton from '@/components/common/LoadingSkeleton'

/**
 * ForecastChart — Apache ECharts SARIMA trend line (Step 4.4).
 *
 * Props:
 *   data      — { dates: string[], actual: number[], forecast7: number[], forecast30: number[] }
 *   isLoading — renders skeleton placeholder
 *
 * When API is not live (VITE_API_BASE_URL unset), renders with MOCK_DATA
 * so the chart is visible from day 0.
 */

const MOCK_DATES = Array.from({ length: 37 }, (_, i) => {
  const d = new Date()
  d.setDate(d.getDate() - 30 + i)
  return d.toISOString().slice(0, 10)
})

const MOCK_ACTUAL = MOCK_DATES.slice(0, 30).map((_, i) =>
  Math.round(120 + Math.sin(i / 3) * 40 + Math.random() * 20)
)

const MOCK_FORECAST7 = [null, ...Array(29).fill(null), ...MOCK_DATES.slice(30).map((_, i) =>
  Math.round(130 + i * 4 + Math.random() * 15)
)]

const MOCK_FORECAST30_UPPER = [
  ...Array(29).fill(null),
  null,
  ...MOCK_DATES.slice(30).map((_, i) => Math.round(145 + i * 5))
]

const MOCK_FORECAST30_LOWER = [
  ...Array(29).fill(null),
  null,
  ...MOCK_DATES.slice(30).map((_, i) => Math.round(115 + i * 3))
]

function buildOption(dates, actual, forecast7, upper, lower) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#131F38',
      borderColor: '#24344F',
      textStyle: { color: '#E8E6DD', fontFamily: 'IBM Plex Mono', fontSize: 11 },
      axisPointer: { lineStyle: { color: '#24344F' } }
    },
    legend: {
      data: ['Historical', '7-Day Forecast', '30-Day Upper', '30-Day Lower'],
      textStyle: { color: '#93A0B8', fontSize: 11 },
      bottom: 0
    },
    grid: { top: 16, right: 16, bottom: 40, left: 48, containLabel: false },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        color: '#93A0B8',
        fontSize: 10,
        fontFamily: 'IBM Plex Mono',
        interval: 6
      },
      axisLine: { lineStyle: { color: '#24344F' } },
      splitLine: { show: false }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: '#93A0B8',
        fontSize: 10,
        fontFamily: 'IBM Plex Mono'
      },
      axisLine: { lineStyle: { color: '#24344F' } },
      splitLine: { lineStyle: { color: '#24344F', type: 'dashed', opacity: 0.4 } }
    },
    series: [
      {
        name: 'Historical',
        type: 'line',
        data: actual,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#C9A227', width: 2 },
        areaStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [{ offset: 0, color: 'rgba(201,162,39,0.15)' }, { offset: 1, color: 'transparent' }]
          }
        }
      },
      {
        name: '7-Day Forecast',
        type: 'line',
        data: forecast7,
        smooth: true,
        symbol: 'circle',
        symbolSize: 4,
        lineStyle: { color: '#D8503A', width: 2, type: 'dashed' },
        itemStyle: { color: '#D8503A' }
      },
      {
        name: '30-Day Upper',
        type: 'line',
        data: upper,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#A98E5C', width: 1, type: 'dotted' },
        stack: 'confidence-band',
        silent: true
      },
      {
        name: '30-Day Lower',
        type: 'line',
        data: lower,
        smooth: true,
        symbol: 'none',
        lineStyle: { color: '#A98E5C', width: 1, type: 'dotted' },
        areaStyle: { color: 'rgba(169, 142, 92, 0.08)' },
        stack: 'confidence-band',
        silent: true
      }
    ]
  }
}

export default function ForecastChart({ data, isLoading }) {
  if (isLoading) {
    return <LoadingSkeleton className="h-56 w-full" />
  }

  const dates    = data?.dates    ?? MOCK_DATES
  const actual   = data?.actual   ?? MOCK_ACTUAL
  const forecast = data?.forecast7 ?? MOCK_FORECAST7
  const upper    = data?.upper    ?? MOCK_FORECAST30_UPPER
  const lower    = data?.lower    ?? MOCK_FORECAST30_LOWER

  return (
    <ReactECharts
      option={buildOption(dates, actual, forecast, upper, lower)}
      style={{ height: '224px', width: '100%' }}
      theme="dark"
    />
  )
}
