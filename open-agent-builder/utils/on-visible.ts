const onVisible = (
  element: HTMLElement,
  callback: () => void,
  threshold = 0.1,
) => {
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        callback();
        observer.disconnect();
      }
    },
    { threshold },
  );

  observer.observe(element);

  return () => {
    observer.disconnect();
  };
};

export default onVisible;

export const waitUntilVisible = (element: HTMLElement, threshold = 0.1) => {
  return new Promise((resolve) => {
    onVisible(element, () => resolve(true), threshold);
  });
};
