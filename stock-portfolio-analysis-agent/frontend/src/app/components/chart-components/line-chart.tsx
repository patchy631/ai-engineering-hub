"use client"

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface LineChartData {
  date: string
  portfolio: number
  spy: number | null | undefined
}

interface LineChartComponentProps {
  data: LineChartData[] | [] | undefined
  size?: "normal" | "small"
}

export function LineChartComponent({ data, size = "normal" }: LineChartComponentProps) {
  const height = size === "small" ? 120 : 192 // h-30 or h-48
  const padding = size === "small" ? "p-2" : "p-4"
  const fontSize = size === "small" ? 8 : 10
  const tooltipFontSize = size === "small" ? "9px" : "11px"
  const legendFontSize = size === "small" ? "9px" : "11px"
  return (
    <div className={`bg-white border border-[#D8D8E5] rounded-xl ${padding}`}>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E8E8EF" />
            <XAxis dataKey="date" stroke="#575758" fontSize={fontSize} fontFamily="Plus Jakarta Sans" />
            <YAxis
              stroke="#575758"
              fontSize={fontSize}
              fontFamily="Plus Jakarta Sans"
              tickFormatter={(value) => `$${(value / 1000).toFixed(0)}K`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "white",
                border: "1px solid #D8D8E5",
                color: "#575758",
                borderRadius: "8px",
                fontSize: tooltipFontSize,
                fontFamily: "Plus Jakarta Sans",
              }}
              formatter={(value: any, name: string) => [
                value != null && typeof value === 'number' ? `$${value.toLocaleString()}` : "N/A",
                name.toLowerCase() === "portfolio" ? "Portfolio" : "SPY",
              ]}
            />
            <Legend
              wrapperStyle={{
                fontSize: legendFontSize,
                fontFamily: "Plus Jakarta Sans",
                fontWeight: 500,
              }}
            />
            <Line type="monotone" dataKey="portfolio" stroke="#FF003C" strokeWidth={2} name="Portfolio" dot={false} />
            <Line type="monotone" dataKey="spy" stroke="#BEC9FF" strokeWidth={2} name="SPY" dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
