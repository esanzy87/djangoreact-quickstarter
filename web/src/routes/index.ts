import React from 'react';

const HomePage = React.lazy(() => import('src/pages/Home'));

const routes = [
  {
    name: 'home',
    path: '/',
    component: HomePage,
    exact: true,
  },
];

export default routes;
