"use client"

import { useState } from "react"
import { Edit2, Check, X, DollarSign, TrendingUp, Wallet, Calendar } from "lucide-react"

interface CashPanelProps {
  totalCash: number
  investedAmount: number
  currentPortfolioValue: number
  onTotalCashChange: (amount: number) => void
  onStateCashChange: (state: any) => void
}

export function CashPanel({ totalCash, investedAmount, currentPortfolioValue, onTotalCashChange, onStateCashChange }: CashPanelProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editValue, setEditValue] = useState(totalCash.toString())

  // const availableCash = totalCash - investedAmount
  const investedPercentage = totalCash > 0 ? (investedAmount / (totalCash + investedAmount)) * 100 : 0
  const fourYearReturn = currentPortfolioValue - investedAmount - totalCash
  const fourYearReturnPercentage = investedAmount > 0 ? (fourYearReturn / investedAmount) * 100 : 0

  const handleEdit = () => {
    setIsEditing(true)
    setEditValue(totalCash.toString())
  }

  const handleSave = () => {
    const newAmount = Number.parseInt(editValue.replace(/,/g, ""))
    if (!isNaN(newAmount) && newAmount >= 0) {
      onTotalCashChange(newAmount)
      onStateCashChange((prevState: any) => ({
        ...prevState,
        available_cash: newAmount,
      }))
    }
    setIsEditing(false)
  }

  const handleCancel = () => {
    setIsEditing(false)
    setEditValue(totalCash.toString())
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  return (
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-6">
        {/* Total Cash */}
        <div className="flex items-center gap-2 group">
          <div className="w-8 h-8 bg-[#FF003C] rounded-full flex items-center justify-center">
            <Wallet size={16} className="text-[#030507]" />
          </div>
          <div>
            <div className="text-xs text-[#575758] font-medium">Total Cash</div>
            {isEditing ? (
              <div className="flex items-center gap-1">
                <input
                  type="text"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  className="w-12 text-sm font-semibold text-[#030507] font-['Roobert']"
                  onKeyDown={(e) => e.key === "Enter" && handleSave()}
                />
                <button onClick={handleSave} className="p-1 text-[#1B606F] hover:bg-[#FF003C]/20 rounded">
                  <Check size={12} />
                </button>
                <button onClick={handleCancel} className="p-1 text-[#575758] hover:bg-[#F0F0F4] rounded">
                  <X size={12} />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-1">
                <span className="text-sm font-semibold text-[#030507] font-['Roobert']">
                  {formatCurrency(totalCash)}
                </span>
                <button
                  onClick={handleEdit}
                  className="p-1 text-[#575758] hover:bg-[#F0F0F4] rounded opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Edit2 size={12} />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Invested Amount */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#BEC9FF] rounded-full flex items-center justify-center">
            <TrendingUp size={16} className="text-[#030507]" />
          </div>
          <div>
            <div className="text-xs text-[#575758] font-medium">Invested</div>
            <div className="text-sm font-semibold text-[#030507] font-['Roobert']">
              {formatCurrency(investedAmount)}
            </div>
          </div>
        </div>

        {/* Current Portfolio Value */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#FFF388] rounded-full flex items-center justify-center">
            <DollarSign size={16} className="text-[#030507]" />
          </div>
          <div>
            <div className="text-xs text-[#575758] font-medium">Portfolio Value</div>
            <div className="text-sm font-semibold text-[#030507] font-['Roobert']">
              {formatCurrency(currentPortfolioValue)}
            </div>
          </div>
        </div>

        {/* 4-Year Return */}
        <div className="flex items-center gap-2">
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center ${
              fourYearReturn >= 0 ? "bg-[#FF003C]" : "bg-red-100"
            }`}
          >
            <Calendar size={16} className={fourYearReturn >= 0 ? "text-[#030507]" : "text-red-600"} />
          </div>
          <div>
            <div className="text-xs text-[#575758] font-medium">4-Year Return</div>
            <div className="flex items-center gap-2">
              <div
                className={`text-sm font-semibold font-['Roobert'] ${
                  fourYearReturn >= 0 ? "text-[#1B606F]" : "text-red-600"
                }`}
              >
                {fourYearReturn >= 0 ? "+" : ""}
                {formatCurrency(fourYearReturn)}
              </div>
              <div className={`text-xs font-medium ${fourYearReturn >= 0 ? "text-[#1B606F]" : "text-red-600"}`}>
                ({fourYearReturn >= 0 ? "+" : ""}
                {fourYearReturnPercentage.toFixed(1)}%)
              </div>
            </div>
          </div>
        </div>

        {/* Available Cash */}
        {/* <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-[#D8D8E5] rounded-full flex items-center justify-center">
            <Wallet size={16} className="text-[#030507]" />
          </div>
          <div>
            <div className="text-xs text-[#575758] font-medium">Available</div>
            <div
              className={`text-sm font-semibold font-['Roobert'] ${
                availableCash < 0 ? "text-red-600" : "text-[#030507]"
              }`}
            >
              {formatCurrency(availableCash)}
            </div>
          </div>
        </div> */}
      </div>

      {/* Investment Progress */}
      <div className="flex items-center gap-3">
        <div className="text-right">
          <div className="text-xs text-[#575758] font-medium">Portfolio Allocation</div>
          <div className="text-sm font-semibold text-[#030507] font-['Roobert']">{investedPercentage.toFixed(1)}%</div>
        </div>
        <div className="w-20 h-2 bg-[#E8E8EF] rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[#FF003C] to-[#BEC9FF] transition-all duration-300"
            style={{ width: `${Math.min(investedPercentage, 100)}%` }}
          />
        </div>
      </div>
    </div>
  )
}
