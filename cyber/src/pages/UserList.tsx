// import * as React from 'react';
// import { useState, useEffect } from 'react';
// import {
//   EuiBasicTable,
//   EuiButton,
//   EuiButtonIcon,
//   EuiFlexGroup,
//   EuiFlexItem,
//   EuiPage,
//   EuiPageBody,
//   EuiPageHeader,
//   EuiTitle,
//   EuiModal,
//   EuiModalHeader,
//   EuiModalHeaderTitle,
//   EuiModalBody,
//   EuiModalFooter,
//   EuiForm,
//   EuiFormRow,
//   EuiFieldText,
//   EuiFieldPassword,
//   EuiSpacer
// } from '@elastic/eui';
// import { userService } from '../services/api';
//
// const UsersList = () => {
//   const [users, setUsers] = useState([]);
//   const [isModalVisible, setIsModalVisible] = useState(false);
//   const [currentUser, setCurrentUser] = useState({ user_id: '', username: '', email: '', role: '', password: '', last_login: '' });
//   const [isEditing, setIsEditing] = useState(false);
//
//   useEffect(() => {
//     fetchUsers();
//   }, []);
//
//   const fetchUsers = async () => {
//     try {
//       const response = await userService.getUsers();
//       setUsers(response.data);
//     } catch (error) {
//       console.error('Error fetching users:', error);
//     }
//   };
//
//   const handleOpenModal = (user = null) => {
//     if (user) {
//       setCurrentUser({ ...user, last_login: ''  });
//       setIsEditing(true);
//     } else {
//       setCurrentUser({ user_id: '', username: '', email: '', role: '', password: '', last_login: ''  });
//       setIsEditing(false);
//     }
//     setIsModalVisible(true);
//   };
//
//   const handleCloseModal = () => {
//     setIsModalVisible(false);
//   };
//
//   const handleInputChange = (e) => {
//     const { name, value } = e.target;
//     setCurrentUser({ ...currentUser, [name]: value });
//   };
//
//   const handleSubmit = async () => {
//     try {
//       if (isEditing) {
//         const { user_id, ...userData } = currentUser;
//         await userService.updateUser(user_id, userData);
//       } else {
//         await userService.createUser(currentUser);
//       }
//       handleCloseModal();
//       fetchUsers();
//     } catch (error) {
//       console.error('Error saving user:', error);
//     }
//   };
//
//   const handleDeleteUser = async (userId) => {
//     try {
//       await userService.deleteUser(userId);
//       fetchUsers();
//     } catch (error) {
//       console.error('Error deleting user:', error);
//     }
//   };
//
//   const columns = [
//     {
//       field: 'user_id',
//       name: 'ID',
//       sortable: true,
//       width: '50px',
//     },
//     {
//       field: 'username',
//       name: 'Username',
//       sortable: true,
//     },
//     {
//       field: 'email',
//       name: 'Email',
//       sortable: true,
//     },
//     {
//       field: 'role',
//       name: 'Role',
//     },
//     {
//       field: 'last_login',
//       name: 'Last Login',
//       render: (last_login) => {
//         return last_login ? new Date(last_login).toLocaleString() : 'Never logged in';
//       },
//     },
//     {
//       field: 'user_id',
//       name: 'Actions',
//       render: (user_id, user) => (
//         <div>
//           <EuiButtonIcon
//             iconType="pencil"
//             aria-label="Edit"
//             onClick={() => handleOpenModal(user)}
//           />
//           &nbsp;
//           <EuiButtonIcon
//             iconType="trash"
//             color="danger"
//             aria-label="Delete"
//             onClick={() => {
//               if (window.confirm('Are you sure you want to delete this user?')) {
//                 handleDeleteUser(user.user_id);
//               }
//             }}
//           />
//         </div>
//       ),
//     },
//   ];
//
//   const modal = isModalVisible ? (
//     <EuiModal onClose={handleCloseModal} style={{ width: '500px' }}>
//       <EuiModalHeader>
//         <EuiModalHeaderTitle>
//           {isEditing ? 'Edit User' : 'Add New User'}
//         </EuiModalHeaderTitle>
//       </EuiModalHeader>
//
//       <EuiModalBody>
//         <EuiForm>
//           <EuiFormRow label="Username">
//             <EuiFieldText
//               name="username"
//               value={currentUser.username}
//               onChange={(e) => handleInputChange(e)}
//             />
//           </EuiFormRow>
//
//           <EuiFormRow label="Email">
//             <EuiFieldText
//               name="email"
//               type="email"
//               value={currentUser.email}
//               onChange={(e) => handleInputChange(e)}
//             />
//           </EuiFormRow>
//
//           <EuiFormRow label="Role">
//             <EuiFieldText
//               name="role"
//               value={currentUser.role || ''}
//               onChange={(e) => handleInputChange(e)}
//             />
//           </EuiFormRow>
//
//           <EuiFormRow label="Password">
//             <EuiFieldPassword
//               name="password"
//               value={currentUser.password || ''}
//               onChange={(e) => handleInputChange(e)}
//             />
//           </EuiFormRow>
//           <EuiFormRow label="Last Login">
//             <EuiFieldText
//               name="last_login"
//               value={currentUser.last_login ? new Date(currentUser.last_login).toLocaleString() : 'Never logged in'}
//               disabled
//             />
//           </EuiFormRow>
//         </EuiForm>
//       </EuiModalBody>
//
//       <EuiModalFooter>
//         <EuiButton onClick={handleCloseModal} fill={false}>
//           Cancel
//         </EuiButton>
//
//         <EuiButton onClick={handleSubmit} fill>
//           {isEditing ? 'Update' : 'Create'}
//         </EuiButton>
//       </EuiModalFooter>
//     </EuiModal>
//   ) : null;
//
//   return (
//     <EuiPage>
//       <EuiPageBody>
//         <EuiPageHeader>
//           <EuiFlexGroup justifyContent="spaceBetween" alignItems="center">
//             <EuiFlexItem grow={false}>
//               <EuiTitle>
//                 <h1>Users Management</h1>
//               </EuiTitle>
//             </EuiFlexItem>
//             <EuiFlexItem grow={false}>
//               <EuiButton
//                 iconType="plusInCircle"
//                 onClick={() => handleOpenModal()}
//                 fill
//               >
//                 Add New User
//               </EuiButton>
//             </EuiFlexItem>
//           </EuiFlexGroup>
//         </EuiPageHeader>
//
//         <EuiSpacer size="l" />
//
//         <EuiBasicTable
//           items={users}
//           columns={columns}
//           tableLayout="fixed"
//         />
//
//         {modal}
//       </EuiPageBody>
//     </EuiPage>
//   );
// };
//
// export default UsersList;

import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  EuiBasicTable,
  EuiButton,
  EuiButtonIcon,
  EuiFlexGroup,
  EuiFlexItem,
  EuiPage,
  EuiPageBody,
  EuiPageHeader,
  EuiTitle,
  EuiModal,
  EuiModalHeader,
  EuiModalHeaderTitle,
  EuiModalBody,
  EuiModalFooter,
  EuiForm,
  EuiFormRow,
  EuiFieldText,
  EuiFieldPassword,
  EuiSpacer,
  EuiSwitch,
  EuiSelect
} from '@elastic/eui';
import { userService } from '../services/api';

const UsersList = () => {
  const [users, setUsers] = useState([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentUser, setCurrentUser] = useState({
    user_id: '',
    username: '',
    email: '',
    role: '',
    password: '',
    last_login: '',
    is_active: true,
    date_joined: ''
  });
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await userService.getUsers();
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleOpenModal = (user = null) => {
    if (user) {
      setCurrentUser({ ...user, password: '' });
      setIsEditing(true);
    } else {
      setCurrentUser({
        user_id: '',
        username: '',
        email: '',
        role: 'user',
        password: '',
        last_login: '',
        is_active: true,
        date_joined: ''
      });
      setIsEditing(false);
    }
    setIsModalVisible(true);
  };

  const handleCloseModal = () => {
    setIsModalVisible(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCurrentUser({ ...currentUser, [name]: value });
  };

  const handleSubmit = async () => {
    try {
      if (isEditing) {
        const { user_id, ...userData } = currentUser;
        await userService.updateUser(user_id, userData);
      } else {
        await userService.createUser(currentUser);
      }
      handleCloseModal();
      fetchUsers();
    } catch (error) {
      console.error('Error saving user:', error);
    }
  };

  const handleDeleteUser = async (userId) => {
    try {
      await userService.deleteUser(userId);
      fetchUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
    }
  };

  const columns = [
    {
      field: 'user_id',
      name: 'ID',
      sortable: true,
      width: '50px',
    },
    {
      field: 'username',
      name: 'Username',
      sortable: true,
    },
    {
      field: 'email',
      name: 'Email',
      sortable: true,
    },
    {
      field: 'role',
      name: 'Role',
    },
    {
      field: 'is_active',
      name: 'Status',
      render: (is_active) => (is_active ? 'Active' : 'Inactive'),
    },
    {
      field: 'last_login',
      name: 'Last Login',
      render: (last_login) => {
        return last_login ? new Date(last_login).toLocaleString() : 'Never logged in';
      },
    },
    {
      field: 'date_joined',
      name: 'Date Joined',
      render: (date_joined) => {
        return date_joined ? new Date(date_joined).toLocaleString() : '';
      },
    },
    {
      field: 'user_id',
      name: 'Actions',
      render: (user_id, user) => (
        <div>
          <EuiButtonIcon
            iconType="pencil"
            aria-label="Edit"
            onClick={() => handleOpenModal(user)}
          />
          &nbsp;
          <EuiButtonIcon
            iconType="trash"
            color="danger"
            aria-label="Delete"
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this user?')) {
                handleDeleteUser(user.user_id);
              }
            }}
          />
        </div>
      ),
    },
  ];

  const modal = isModalVisible ? (
    <EuiModal onClose={handleCloseModal} style={{ width: '500px' }}>
      <EuiModalHeader>
        <EuiModalHeaderTitle>
          {isEditing ? 'Edit User' : 'Add New User'}
        </EuiModalHeaderTitle>
      </EuiModalHeader>

      <EuiModalBody>
        <EuiForm>
          <EuiFormRow label="Username">
            <EuiFieldText
              name="username"
              value={currentUser.username}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Email">
            <EuiFieldText
              name="email"
              type="email"
              value={currentUser.email}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Role">
            <EuiSelect
              name="role"
              options={[
                { value: 'admin', text: 'Administrator' },
                { value: 'analyst', text: 'Security Analyst' },
                { value: 'manager', text: 'Security Manager' },
                { value: 'user', text: 'Regular User' }
              ]}
              value={currentUser.role || ''}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Password">
            <EuiFieldPassword
              name="password"
              value={currentUser.password || ''}
              onChange={(e) => handleInputChange(e)}
            />
          </EuiFormRow>

          <EuiFormRow label="Active">
            <EuiSwitch
              name="is_active"
              label="User is active"
              checked={currentUser.is_active}
              onChange={(e) => handleInputChange({
                target: {
                  name: 'is_active',
                  value: e.target.checked
                }
              })}
            />
          </EuiFormRow>

          {isEditing && (
            <>
              <EuiFormRow label="Last Login">
                <EuiFieldText
                  name="last_login"
                  value={currentUser.last_login ? new Date(currentUser.last_login).toLocaleString() : 'Never logged in'}
                  disabled
                />
              </EuiFormRow>

              <EuiFormRow label="Date Joined">
                <EuiFieldText
                  name="date_joined"
                  value={currentUser.date_joined ? new Date(currentUser.date_joined).toLocaleString() : ''}
                  disabled
                />
              </EuiFormRow>
            </>
          )}
        </EuiForm>
      </EuiModalBody>

      <EuiModalFooter>
        <EuiButton onClick={handleCloseModal} fill={false}>
          Cancel
        </EuiButton>

        <EuiButton onClick={handleSubmit} fill>
          {isEditing ? 'Update' : 'Create'}
        </EuiButton>
      </EuiModalFooter>
    </EuiModal>
  ) : null;

  return (
    <EuiPage>
      <EuiPageBody>
        <EuiPageHeader>
          <EuiFlexGroup justifyContent="spaceBetween" alignItems="center">
            <EuiFlexItem grow={false}>
              <EuiTitle>
                <h1>Users Management</h1>
              </EuiTitle>
            </EuiFlexItem>
            <EuiFlexItem grow={false}>
              <EuiButton
                iconType="plusInCircle"
                onClick={() => handleOpenModal()}
                fill
              >
                Add New User
              </EuiButton>
            </EuiFlexItem>
          </EuiFlexGroup>
        </EuiPageHeader>

        <EuiSpacer size="l" />

        <EuiBasicTable
          items={users}
          columns={columns}
          tableLayout="fixed"
        />

        {modal}
      </EuiPageBody>
    </EuiPage>
  );
};

export default UsersList;