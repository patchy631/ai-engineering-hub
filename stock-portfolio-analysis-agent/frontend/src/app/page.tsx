"use client"

import { useEffect, useState } from "react"
import { PromptPanel } from "./components/prompt-panel"
import { GenerativeCanvas } from "./components/generative-canvas"
import { ComponentTree } from "./components/component-tree"
import { CashPanel } from "./components/cash-panel"
import { useCoAgent, useCoAgentStateRender, useCopilotAction, useCopilotReadable } from "@copilotkit/react-core"
import { BarChartComponent } from "@/app/components/chart-components/bar-chart"
import { LineChartComponent } from "@/app/components/chart-components/line-chart"
import { AllocationTableComponent } from "@/app/components/chart-components/allocation-table"
import { useCopilotChatSuggestions } from "@copilotkit/react-ui"
import { INVESTMENT_SUGGESTION_PROMPT } from "@/utils/prompts"
import { ToolLogs } from "./components/tool-logs"

export interface PortfolioState {
  id: string
  trigger: string
  investmentAmount?: number
  currentPortfolioValue?: number
  performanceData: Array<{
    date: string
    portfolio: number
    spy: number
  }>
  allocations: Array<{
    ticker: string
    allocation: number
    currentValue: number
    totalReturn: number
  }>
  returnsData: Array<{
    ticker: string
    return: number
  }>
  bullInsights: Array<{
    title: string
    description: string
    emoji: string
  }>
  bearInsights: Array<{
    title: string
    description: string
    emoji: string
  }>
  totalReturns: number
}

export interface SandBoxPortfolioState {
  performanceData: Array<{
    date: string
    portfolio: number
    spy: number
  }>
}
export interface InvestmentPortfolio {
  ticker: string
  amount: number
}


export default function OpenStocksCanvas() {
  const [currentState, setCurrentState] = useState<PortfolioState>({
    id: "",
    trigger: "",
    performanceData: [],
    allocations: [],
    returnsData: [],
    bullInsights: [],
    bearInsights: [],
    currentPortfolioValue: 0,
    totalReturns: 0
  })
  const [sandBoxPortfolio, setSandBoxPortfolio] = useState<SandBoxPortfolioState[]>([])
  const [selectedStock, setSelectedStock] = useState<string | null>(null)
  const [showComponentTree, setShowComponentTree] = useState(false)
  const [totalCash, setTotalCash] = useState(1000000)
  const [investedAmount, setInvestedAmount] = useState(0)

  const { state, setState } = useCoAgent({
    name: "crewaiAgent",
    initialState: {
      available_cash: totalCash,
      investment_summary: {} as any,
      investment_portfolio: [] as InvestmentPortfolio[]
    }
  })

  useCoAgentStateRender({
    name: "crewaiAgent",
    render: ({state}) => <ToolLogs logs={state.tool_logs} />
  })

  useCopilotAction({
    name: "render_standard_charts_and_table",
    description: "This is an action to render a standard chart and table. The chart can be a bar chart or a line chart. The table can be a table of data.",
    renderAndWaitForResponse: ({ args, respond, status }) => {
      useEffect(() => {
        console.log(args, "argsargsargsargsargsaaa")
      }, [args])
      return (
        <>
          {(args?.investment_summary?.percent_allocation_per_stock && args?.investment_summary?.percent_return_per_stock && args?.investment_summary?.performanceData) &&
            <>
              <div className="flex flex-col gap-4">
                <LineChartComponent data={args?.investment_summary?.performanceData} size="small" />
                <BarChartComponent data={Object.entries(args?.investment_summary?.percent_return_per_stock).map(([ticker, return1]) => ({
                  ticker,
                  return: return1 as number
                }))} size="small" />
                <AllocationTableComponent allocations={Object.entries(args?.investment_summary?.percent_allocation_per_stock).map(([ticker, allocation]) => ({
                  ticker,
                  allocation: allocation as number,
                  currentValue: args?.investment_summary.final_prices[ticker] * args?.investment_summary.holdings[ticker],
                  totalReturn: args?.investment_summary.percent_return_per_stock[ticker]
                }))} size="small" />

              </div>

              <button hidden={status == "complete"}
                className="mt-4 rounded-full px-6 py-2 bg-green-50 text-green-700 border border-green-200 shadow-sm hover:bg-green-100 transition-colors font-semibold text-sm"
                onClick={() => {
                  debugger
                  if (respond) {
                    setTotalCash(args?.investment_summary?.cash)
                    setCurrentState({
                      ...currentState,
                      returnsData: Object.entries(args?.investment_summary?.percent_return_per_stock).map(([ticker, return1]) => ({
                        ticker,
                        return: return1 as number
                      })),
                      allocations: Object.entries(args?.investment_summary?.percent_allocation_per_stock).map(([ticker, allocation]) => ({
                        ticker,
                        allocation: allocation as number,
                        currentValue: args?.investment_summary?.final_prices[ticker] * args?.investment_summary?.holdings[ticker],
                        totalReturn: args?.investment_summary?.percent_return_per_stock[ticker]
                      })),
                      performanceData: args?.investment_summary?.performanceData,
                      bullInsights: args?.insights?.bullInsights || [],
                      bearInsights: args?.insights?.bearInsights || [],
                      currentPortfolioValue: args?.investment_summary?.total_value,
                      totalReturns: (Object.values(args?.investment_summary?.returns) as number[])
                        .reduce((acc, val) => acc + val, 0)
                    })
                    setInvestedAmount(
                      (Object.values(args?.investment_summary?.total_invested_per_stock) as number[])
                        .reduce((acc, val) => acc + val, 0)
                    )
                    setState({
                      ...state,
                      available_cash: totalCash,
                    })
                    respond("Data rendered successfully. Provide summary of the investments by not making any tool calls")
                  }
                }}
              >
                Accept
              </button>
              <button hidden={status == "complete"}
                className="rounded-full px-6 py-2 bg-red-50 text-red-700 border border-red-200 shadow-sm hover:bg-red-100 transition-colors font-semibold text-sm ml-2"
                onClick={() => {
                  debugger
                  if (respond) {
                    respond("Data rendering rejected. Just give a summary of the rejected investments by not making any tool calls")
                  }
                }}
              >
                Reject
              </button>
            </>
          }

        </>

      )
    }
  })

  useCopilotAction({
    name: "render_custom_charts",
    renderAndWaitForResponse: ({ args, respond, status }) => {
      return (
        <>
          <LineChartComponent data={args?.investment_summary?.performanceData} size="small" />
          <button hidden={status == "complete"}
            className="mt-4 rounded-full px-6 py-2 bg-green-50 text-green-700 border border-green-200 shadow-sm hover:bg-green-100 transition-colors font-semibold text-sm"
            onClick={() => {
              debugger
              if (respond) {
                setSandBoxPortfolio([...sandBoxPortfolio, {
                  performanceData: args?.investment_summary?.performanceData.map((item: any) => ({
                    date: item.date,
                    portfolio: item.portfolio,
                    spy: item.spy
                  })) || []
                }])
                respond("Data rendered successfully. Provide summary of the investments")
              }
            }}
          >
            Accept
          </button>
          <button hidden={status == "complete"}
            className="rounded-full px-6 py-2 bg-red-50 text-red-700 border border-red-200 shadow-sm hover:bg-red-100 transition-colors font-semibold text-sm ml-2"
            onClick={() => {
              debugger
              if (respond) {
                respond("Data rendering rejected. Just give a summary of the rejected investments")
              }
            }}
          >
            Reject
          </button>
        </>
      )
    }
  })

  useCopilotReadable({
    description: "This is the current state of the portfolio",
    value: JSON.stringify(state.investment_portfolio)
  })

  useCopilotChatSuggestions({
    available: selectedStock ? "disabled" : "enabled",
    instructions: INVESTMENT_SUGGESTION_PROMPT,
  },
    [selectedStock])

  // const toggleComponentTree = () => {
  //   setShowComponentTree(!showComponentTree)
  // }

  // const availableCash = totalCash - investedAmount
  // const currentPortfolioValue = currentState.currentPortfolioValue || investedAmount


  useEffect(() => {
    getBenchmarkData()
  }, [])

  function getBenchmarkData() {
    let result: PortfolioState = {
      id: "aapl-nvda",
      trigger: "apple nvidia",
      performanceData: [
        { date: "Jan 2023", portfolio: 10000, spy: 10000 },
        { date: "Mar 2023", portfolio: 10200, spy: 10200 },
        { date: "Jun 2023", portfolio: 11000, spy: 11000 },
        { date: "Sep 2023", portfolio: 10800, spy: 10800 },
        { date: "Dec 2023", portfolio: 11500, spy: 11500 },
        { date: "Mar 2024", portfolio: 12200, spy: 12200 },
        { date: "Jun 2024", portfolio: 12800, spy: 12800 },
        { date: "Sep 2024", portfolio: 13100, spy: 13100 },
        { date: "Dec 2024", portfolio: 13600, spy: 13600 },
      ],
      allocations: [],
      returnsData: [],
      bullInsights: [],
      bearInsights: [],
      totalReturns: 0,
      currentPortfolioValue: totalCash
    }
    setCurrentState(result)
  }



  return (
    <div className="h-screen bg-[#FAFCFA] flex overflow-hidden">
      {/* Left Panel - Prompt Input */}
      <div className="w-85 border-r border-[#D8D8E5] bg-white flex-shrink-0">
        <PromptPanel availableCash={totalCash} />
      </div>

      {/* Center Panel - Generative Canvas */}
      <div className="flex-1 relative min-w-0">
        {/* Top Bar with Cash Info */}
        <div className="absolute top-0 left-0 right-0 bg-white border-b border-[#D8D8E5] p-4 z-10">
          <CashPanel
            totalCash={totalCash}
            investedAmount={investedAmount}
            currentPortfolioValue={(totalCash + investedAmount + currentState.totalReturns) || 0}
            onTotalCashChange={setTotalCash}
            onStateCashChange={setState}
          />
        </div>

        {/* <div className="absolute top-4 right-4 z-20">
          <button
            onClick={toggleComponentTree}
            className="px-3 py-1 text-xs font-semibold text-[#575758] bg-white border border-[#D8D8E5] rounded-md hover:bg-[#F0F0F4] transition-colors"
          >
            {showComponentTree ? "Hide Tree" : "Show Tree"}
          </button>
        </div> */}

        <div className="pt-20 h-full">
          <GenerativeCanvas setSelectedStock={setSelectedStock} portfolioState={currentState} sandBoxPortfolio={sandBoxPortfolio} setSandBoxPortfolio={setSandBoxPortfolio} />
        </div>
      </div>

      {/* Right Panel - Component Tree (Optional) */}
      {showComponentTree && (
        <div className="w-64 border-l border-[#D8D8E5] bg-white flex-shrink-0">
          <ComponentTree portfolioState={currentState} />
        </div>
      )}
    </div>
  )
}
