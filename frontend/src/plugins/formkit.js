import { plugin, defaultConfig } from '@formkit/vue'
import { generateClasses } from '@formkit/themes'

// Tailwind CSS theme configuration for FormKit
const config = defaultConfig({
  theme: 'genesis',
  config: {
    classes: generateClasses({
      global: {
        outer: 'mb-5',
        wrapper: 'space-y-2',
        label: 'block text-sm font-medium text-gray-700 mb-1',
        inner: 'relative',
        input: 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
        help: 'text-xs text-gray-500 mt-1',
        messages: 'list-none p-0 mt-1 space-y-1',
        message: 'text-red-500 mb-1 text-xs',
      },
      button: {
        input: 'inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed',
      },
      submit: {
        input: 'inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed',
      },
      text: {
        input: 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
      },
      email: {
        input: 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
      },
      number: {
        input: 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
      },
      textarea: {
        input: 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
      },
      select: {
        input: 'block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm',
      },
      checkbox: {
        wrapper: 'flex items-center',
        input: 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded',
        label: 'ml-2 block text-sm text-gray-900',
      },
      radio: {
        wrapper: 'flex items-center',
        input: 'h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300',
        label: 'ml-2 block text-sm text-gray-900',
      },
    })
  }
})

export default config