import React, { useState, useEffect } from 'react';
import {
  EuiBasicTable,
  EuiButton,
  EuiFormRow,
  EuiFieldText,
  EuiSpacer,
  EuiModal,
  EuiModalBody,
  EuiModalFooter,
  EuiModalHeader,
  EuiModalHeaderTitle,
  EuiPageHeader,
  EuiPanel,
  EuiSelect,
  EuiConfirmModal,
} from '@elastic/eui';
import { userService } from '../services/api';

// Define user interface
interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'analyst' | 'user' | 'manager';
  status: 'Active' | 'Inactive';
  is_active: boolean;
  last_login: string;
  date_joined: string;
  password: string;
}

interface BackendUser {
  user_id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  password: string;
  last_login: string;
  date_joined: string;
}

const UserList: React.FC = () => {
  // State for users data
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // State for modal and form
  const [isModalVisible, setIsModalVisible] = useState<boolean>(false);
  const [isDeleteModalVisible, setIsDeleteModalVisible] = useState<boolean>(false);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [formData, setFormData] = useState<Omit<User, 'id'>>({
    username: '',
    email: '',
    role: 'user',
    status: 'Active',
    is_active: true,
    last_login: '',
    date_joined: '',
    password: '',
  });

  // Fetch users data
  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const response = await userService.getUsers();
      // Transform backend data format to match frontend User interface
      const transformedData = response.data.map((user: BackendUser) => ({
        id: user.user_id.toString(),
        username: user.username,
        email: user.email,
        role: user.role as User['role'],
        status: user.is_active ? 'Active' : 'Inactive',
        is_active: user.is_active,
        last_login: user.last_login || '',
        date_joined: user.date_joined || '',
        password: user.password,
      }));


      setUsers(transformedData);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Create new user
  const createUser = async () => {
    try {
      const userData = {
        username: formData.username,
        email: formData.email,
        role: formData.role,
        is_active: formData.status === 'Active',
        password: formData.password,
      };

      const response = await userService.createUser(userData);

      // Add the new user to the list
      const newUser: User = {
        id: response.data.user_id.toString(),
        username: response.data.username,
        email: response.data.email,
        role: response.data.role as User['role'],
        status: response.data.is_active ? 'Active' : 'Inactive',
        is_active: response.data.is_active,
        password: response.data.password,
        last_login: response.data.last_login,
        date_joined: response.data.date_joined,
      };

      setUsers([...users, newUser]);
      closeModal();
    } catch (error) {
      console.error('Failed to create user:', error);
    }
  };

  // Update existing user
// Update existing user
  const updateUser = async () => {
    if (!currentUser) return;
    try {
      const userData = {
        username: formData.username,
        email: formData.email,
        role: formData.role,
        is_active: formData.status === 'Active',
      };

      // Only include password if it was changed (not empty)
      if (formData.password.trim() !== '') {
        userData['password'] = formData.password;
      }

      await userService.updateUser(currentUser.id, userData);

      // Update the user in the list
      const updatedUsers = users.map(user =>
        user.id === currentUser.id
          ? {
              ...user,
              username: formData.username,
              email: formData.email,
              role: formData.role,
              status: formData.status,
              is_active: formData.status === 'Active'
            }
          : user
      );

      setUsers(updatedUsers);
      closeModal();
    } catch (error) {
      console.error('Failed to update user:', error);
    }
  };

  // Delete user
  const deleteUser = async () => {
    if (!currentUser) return;

    try {
      await userService.deleteUser(currentUser.id);

      // Remove the user from the list
      const filteredUsers = users.filter(
        user => user.id !== currentUser.id
      );

      setUsers(filteredUsers);
      closeDeleteModal();
    } catch (error) {
      console.error('Failed to delete user:', error);
    }
  };

  // Handle form input changes
  const handleInputChange = (field: string, value: any) => {
    setFormData({
      ...formData,
      [field]: value,
    });
  };

  // Open modal for creating new user
  const openCreateModal = () => {
    setCurrentUser(null);
    setFormData({
      username: '',
      email: '',
      role: 'user',
      status: 'Active',
      is_active: true,
      last_login: '',
      date_joined: '',
      password: '',
    });

    setIsModalVisible(true);
  };

  // Open modal for editing existing user
  const openEditModal = (user: User) => {
    setCurrentUser(user);
    setFormData({
      username: user.username,
      email: user.email,
      role: user.role,
      status: user.status,
      is_active: user.is_active,
      last_login: user.last_login,
      date_joined: user.date_joined,
      password: user.password,
    });

    setIsModalVisible(true);
  };

  // Open delete confirmation modal
  const openDeleteModal = (user: User) => {
    setCurrentUser(user);
    setIsDeleteModalVisible(true);
  };

  // Close modals
  const closeModal = () => {
    setIsModalVisible(false);
    setCurrentUser(null);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalVisible(false);
    setCurrentUser(null);
  };

  // Table columns configuration
  const columns = [
    {
      field: 'id',
      name: 'ID',
      sortable: true,
      width: '70px',
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
      sortable: true,
      render: (role: User['role']) => {
        const colors = {
          user: 'primary' as 'primary',
          analyst: 'success' as 'success',
          manager: 'warning' as 'warning',
          admin: 'danger' as 'danger',
        };
        return (
          <EuiButton
            size="s"
            color={colors[role]}
            fill
          >
            {role.charAt(0).toUpperCase() + role.slice(1)}
          </EuiButton>
        );
      },
    },
    {
      field: 'status',
      name: 'Status',
      sortable: true,
      render: (status: User['status']) => {
      const colors = {
          Active: 'success' as 'success',
          Inactive: 'danger' as 'danger',
        };
        return (
          <EuiButton
            size="s"
            color={colors[status]}
            fill
          >
            {status ? status : ''}
          </EuiButton>
        );
      },
    },
    {
      field: 'last_login',
      name: 'Last Login',
      sortable: true,
      render: (lastLogin: string) => {
        return lastLogin ? new Date(lastLogin).toLocaleString() : 'Never';
      }
    },
    {
      field: 'date_joined',
      name: 'Date Joined',
      sortable: true,
      render: (dateJoined: string) => {
        return dateJoined ? new Date(dateJoined).toLocaleString() : 'Unknown';
      }
    },
    {
      name: 'Actions',
      actions: [
        {
          name: 'Edit',
          description: 'Edit this user',
          icon: 'pencil',
          type: 'icon',
          onClick: (user: User) => openEditModal(user),
        },
        {
          name: 'Delete',
          description: 'Delete this user',
          icon: 'trash',
          type: 'icon',
          color: 'danger' as 'danger',
          onClick: (user: User) => openDeleteModal(user),
        },
      ],
    } as any,
  ];

  return (
    <div style={{ padding: '24px' }}>
      <EuiPageHeader
        pageTitle="Users Management"
        rightSideItems={[
          <EuiButton
            fill
            iconType="plusInCircle"
            onClick={openCreateModal}
          >
            Create User
          </EuiButton>,
        ]}
      />

      <EuiSpacer size="l" />

      <EuiPanel>
        <EuiBasicTable
          items={users}
          columns={columns}
          loading={isLoading}
          noItemsMessage="No users found"
        />
      </EuiPanel>

      {/* Create/Edit Modal */}
      {isModalVisible && (
        <EuiModal onClose={closeModal}>
          <EuiModalHeader>
            <EuiModalHeaderTitle>
              {currentUser ? 'Edit User' : 'Create New User'}
            </EuiModalHeaderTitle>
          </EuiModalHeader>

<EuiModalBody>
            <EuiFormRow label="Username" labelType="label">
              <EuiFieldText
                placeholder="Enter username"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
                required
              />
            </EuiFormRow>

            <EuiFormRow label="Email" labelType="label">
              <EuiFieldText
                placeholder="Enter email address"
                value={formData.email}
                onChange={(e) => handleInputChange('email', e.target.value)}
                required
              />
            </EuiFormRow>

            <EuiFormRow label="Password" labelType="label">
              <EuiFieldText
                type="password"
                placeholder="Enter password"
                value={formData.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
                required={!currentUser}
              />
            </EuiFormRow>

            <EuiFormRow label="Role" labelType="label">
              <EuiSelect
                options={[
                  { value: 'user', text: 'User' },
                  { value: 'analyst', text: 'Analyst' },
                  { value: 'manager', text: 'Manager' },
                  { value: 'admin', text: 'Admin' },
                ]}
                value={formData.role}
                onChange={(e) => handleInputChange('role', e.target.value)}
              />
            </EuiFormRow>

            <EuiFormRow label="Status" labelType="label">
              <EuiSelect
                options={[
                  { value: 'Active', text: 'Active' },
                  { value: 'Inactive', text: 'Inactive' },
                ]}
                value={formData.status}
                onChange={(e) => {
                  const status = e.target.value;
                  handleInputChange('status', status);
                  handleInputChange('is_active', status === 'Active');
                }}
              />
            </EuiFormRow>

            {currentUser && (
              <>
                <EuiFormRow label="Last Login" labelType="label">
                  <EuiFieldText
                    value={formData.last_login}
                    disabled
                  />
                </EuiFormRow>

                <EuiFormRow label="Date Joined" labelType="label">
                  <EuiFieldText
                    value={formData.date_joined}
                    disabled
                  />
                </EuiFormRow>
              </>
            )}
          </EuiModalBody>

          <EuiModalFooter>
            <EuiButton onClick={closeModal}>Cancel</EuiButton>
            <EuiButton
              fill
              onClick={currentUser ? updateUser : createUser}
            >
              {currentUser ? 'Update' : 'Create'}
            </EuiButton>
          </EuiModalFooter>
        </EuiModal>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteModalVisible && (
        <EuiConfirmModal
          title="Delete User"
          onCancel={closeDeleteModal}
          onConfirm={deleteUser}
          cancelButtonText="Cancel"
          confirmButtonText="Delete"
          buttonColor="danger"
        >
          <p>Are you sure you want to delete user "{currentUser?.username}"?</p>
          <p>This action cannot be undone.</p>
        </EuiConfirmModal>
      )}
    </div>
  );
};

export default UserList;