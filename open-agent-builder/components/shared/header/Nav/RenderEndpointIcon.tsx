"use client";

import EndpointsScrape from "@/components/app/(home)/sections/endpoints/EndpointsScrape/EndpointsScrape";
import { ComponentProps } from "react";
import { useMediaQuery } from "usehooks-ts";

export const RenderEndpointIcon = ({
  icon: Icon,
  ...props
}: { icon: typeof EndpointsScrape } & ComponentProps<
  typeof EndpointsScrape
>) => {
  const isMobile = useMediaQuery("(max-width: 996px)");

  return <Icon {...props} size={isMobile ? 24 : 20} />;
};
