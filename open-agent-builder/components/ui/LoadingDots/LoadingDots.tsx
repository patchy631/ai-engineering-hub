import s from "./LoadingDots.module.css";
import cn from "classnames";

const LoadingDots = ({ className }: { className?: string }) => {
  return (
    <span className={cn(s.root, className)}>
      <span />
      <span />
      <span />
    </span>
  );
};

export default LoadingDots;
