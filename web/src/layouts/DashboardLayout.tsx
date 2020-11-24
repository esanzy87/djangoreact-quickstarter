import React from 'react';

function DashboardLayout(props) {
  const { children } = props;

  return (
    <>
      <header>
        {/* header content */}
      </header>
      <main>
        {children}
      </main>
      <footer>
        {/* footer content */}
      </footer>
    </>
  );
}

export default DashboardLayout;
