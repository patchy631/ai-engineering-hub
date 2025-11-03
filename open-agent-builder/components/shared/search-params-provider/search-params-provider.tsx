"use client";

import React, { createContext, useContext, ReactNode } from "react";

type SearchParamsContextType = { [key: string]: string | string[] | undefined };

const SearchParamsContext = createContext<SearchParamsContextType | null>(null);

export const SearchParamsProvider = ({
  children,
  params,
}: {
  children: ReactNode;
  params: SearchParamsContextType;
}) => {
  return (
    <SearchParamsContext.Provider value={params}>
      {children}
    </SearchParamsContext.Provider>
  );
};

export const useSearchParamsContext = () => {
  const context = useContext(SearchParamsContext);

  if (!context) {
    throw new Error(
      "useSearchParamsContext must be used within a SearchParamsProvider",
    );
  }

  return context;
};
