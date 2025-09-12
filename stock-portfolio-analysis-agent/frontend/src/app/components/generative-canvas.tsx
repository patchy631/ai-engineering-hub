"use client"

import { LineChartComponent } from "./chart-components/line-chart"
import { AllocationTableComponent } from "./chart-components/allocation-table"
import { InsightCardComponent } from "./chart-components/insight-card"
import { SectionTitle } from "./chart-components/section-title"
import { BarChartComponent } from "./chart-components/bar-chart"
import type { PortfolioState, SandBoxPortfolioState } from "../page"

interface GenerativeCanvasProps {
  portfolioState: PortfolioState
  setSelectedStock: (stock: string) => void
  sandBoxPortfolio: SandBoxPortfolioState[]
  setSandBoxPortfolio: (portfolio: SandBoxPortfolioState[]) => void
}

export function GenerativeCanvas({ portfolioState, setSelectedStock, sandBoxPortfolio, setSandBoxPortfolio }: GenerativeCanvasProps) {
  return (
    <div className="h-full overflow-auto">
      <div className="p-4 space-y-4 max-w-none">
        {/* Performance Section */}
        <div>
          <SectionTitle title="Performance" />
          <div className="mt-3">
            {portfolioState?.performanceData?.length === 0 ? (
              <div className="text-center text-sm text-gray-400 py-6">No performance data to show.</div>
            ) : (
              <LineChartComponent
                data={
                  (portfolioState?.performanceData || []).map(d => ({
                    ...d,
                    portfolio: d.portfolio ?? 0,
                    spy: d.spy,
                  }))
                }
              />
            )}
          </div>
        </div>

        {/* Allocation and Returns Section */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <SectionTitle title="Allocation" />
            <div className="mt-3">
              {portfolioState.allocations.length === 0 ? (
                <div className="text-center text-sm text-gray-400 py-6">No allocation data to show.</div>
              ) : (
                <AllocationTableComponent
                  allocations={
                    (portfolioState?.allocations || []).map(a => ({
                      ...a,
                      allocation: Number(a.allocation),
                    }))
                  }
                />
              )}
            </div>
          </div>

          <div>
            <SectionTitle title="Returns" />
            <div className="mt-3">
              {portfolioState.returnsData.length === 0 ? (
                <div className="text-center text-sm text-gray-400 py-6">No returns data to show.</div>
              ) : (
                <BarChartComponent data={portfolioState?.returnsData || []} onClick={setSelectedStock} />
              )}
            </div>
          </div>
        </div>

        {/* Insights Section */}
        <div>
          <SectionTitle title="Market Insights" />
          <div className="mt-3 grid grid-cols-2 gap-4">
            {/* Bull Insights */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">🐂</span>
                <h3 className="text-sm font-semibold text-[#1B606F] font-['Roobert']">BULL CASE</h3>
              </div>
              <div className="space-y-3">
                {portfolioState.bullInsights.length === 0 ? (
                  <div className="text-center text-sm text-gray-400 py-6">No bull case insights.</div>
                ) : (
                  portfolioState.bullInsights.map((insight, index) => (
                    <InsightCardComponent key={`bull-${index}`} insight={insight} type="bull" />
                  ))
                )}
              </div>
            </div>

            {/* Bear Insights */}
            <div>
              <div className="flex items-center gap-2 mb-3">
                <span className="text-lg">🐻</span>
                <h3 className="text-sm font-semibold text-red-600 font-['Roobert']">BEAR CASE</h3>
              </div>
              <div className="space-y-3">
                {portfolioState.bearInsights.length === 0 ? (
                  <div className="text-center text-sm text-gray-400 py-6">No bear case insights.</div>
                ) : (
                  portfolioState.bearInsights.map((insight, index) => (
                    <InsightCardComponent key={`bear-${index}`} insight={insight} type="bear" />
                  ))
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Custom Charts */}
        <div hidden={sandBoxPortfolio?.length == 0}>
          <SectionTitle title="Custom Charts" />
          <div className="mt-3">
            {sandBoxPortfolio?.length === 0 ? (
              <div className="text-center text-sm text-gray-400 py-6">No performance data to show.</div>
            ) : (
              <LineChartComponent
                data={
                  (portfolioState?.performanceData || []).map(d => ({
                    ...d,
                    portfolio: d.portfolio ?? 0,
                    spy: d.spy,
                  }))
                }
              />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
