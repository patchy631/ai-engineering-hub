"use client";

import { ComponentProps } from "react";

import EndpointsScrape from "@/components/app/(home)/sections/endpoints/EndpointsScrape/EndpointsScrape";

export default function EndpointsMap(
  props: ComponentProps<typeof EndpointsScrape>,
) {
  return <EndpointsScrape {...props} disabledCells={[1, 2, 3, 7, 9, 12, 15]} />;
}
