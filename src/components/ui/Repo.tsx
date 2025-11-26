export default function Repo({
  name,
  body,
  language,
  languageColor,
  starCount,
  forkCount,
  isPublic,
  updatedAt,
}: {
  name: string;
  body: string;
  language?: string;
  languageColor?: string;
  starCount: number;
  forkCount: number;
  isPublic: boolean;
  updatedAt: string;
}) {
  return (
    <div
      className={
        "relative w-80 cursor-pointer overflow-hidden rounded-lg border p-4 transition-colors" +
        // light styles
        " border-gray-300 bg-white hover:bg-gray-50" +
        // dark styles
        " dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-750"
      }
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <svg
            className="w-4 h-4 text-gray-600 dark:text-gray-400"
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M10 2L15 7v11H5V7l5-5z"
              clipRule="evenodd"
            />
          </svg>
          <h3 className="text-sm font-semibold text-blue-600 dark:text-blue-400 hover:underline">
            {name}
          </h3>
        </div>
        <span className="text-xs px-2 py-1 rounded-full border border-gray-300 dark:border-gray-600 text-gray-600 dark:text-gray-400">
          {isPublic ? "Public" : "Private"}
        </span>
      </div>

      <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
        {body}
      </p>

      <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <div className="flex items-center gap-4">
          {language && (
            <div className="flex items-center gap-1">
              <div
                className={`w-3 h-3 rounded-full`}
                style={{ backgroundColor: languageColor || "#3178c6" }}
              ></div>
              <span>{language}</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span>{starCount}</span>
          </div>
          <div className="flex items-center gap-1">
            <svg
              className="w-3 h-3"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"
              />
            </svg>
            <span>{forkCount}</span>
          </div>
        </div>
        <span>Updated {updatedAt}</span>
      </div>
    </div>
  );
}
