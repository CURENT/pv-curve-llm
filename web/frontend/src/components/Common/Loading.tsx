interface Props {
  text?: string;
  size?: "sm" | "md" | "lg";
}

export default function Loading({ text, size = "md" }: Props) {
  const sizeMap = { sm: "w-4 h-4", md: "w-6 h-6", lg: "w-10 h-10" };
  return (
    <div className="flex flex-col items-center justify-center gap-3 p-8">
      <div
        className={`${sizeMap[size]} border-2 border-indigo-200 dark:border-indigo-800 border-t-indigo-600 dark:border-t-indigo-400 rounded-full animate-spin`}
      />
      {text && (
        <p className="text-sm text-gray-500 dark:text-gray-400">{text}</p>
      )}
    </div>
  );
}
