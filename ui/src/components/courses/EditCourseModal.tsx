import {
    Modal,
    Stack,
    TextInput,
    Textarea,
    Group,
    Button,
} from '@mantine/core';

interface EditCourseModalProps {
    opened: boolean;
    onClose: () => void;
    courseTitle: string;
    courseDescription: string;
    onTitleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    onDescriptionChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
    onSubmit: (e: React.FormEvent) => void;
    loading: boolean;
    // File upload props (optional - for future implementation by students)
    selectedFile?: File | null;
    onFileChange?: (file: File | null) => void;
    onRemoveImage?: () => void;
    isRemoving?: boolean;
    currentFileUrl?: string | null;
    currentFileName?: string | null;
}

/**
 * Modal for editing course details
 * Note: File upload functionality will be implemented by students
 */
export default function EditCourseModal({
    opened,
    onClose,
    courseTitle,
    courseDescription,
    onTitleChange,
    onDescriptionChange,
    onSubmit,
    loading,
}: EditCourseModalProps) {
    return (
        <Modal opened={opened} onClose={onClose} title="Edit Course" centered>
            <form onSubmit={onSubmit}>
                <Stack gap="md">
                    <TextInput
                        label="Course Title"
                        placeholder="Enter course title"
                        value={courseTitle}
                        onChange={onTitleChange}
                        required
                        disabled={loading}
                        autoFocus
                    />
                    <Textarea
                        label="Description"
                        placeholder="Enter course description (optional)"
                        value={courseDescription}
                        onChange={onDescriptionChange}
                        disabled={loading}
                        rows={4}
                    />
                    {/* File upload functionality will be implemented by students */}
                    <Group justify="flex-end">
                        <Button
                            variant="subtle"
                            onClick={onClose}
                            disabled={loading}
                        >
                            Cancel
                        </Button>
                        <Button type="submit" loading={loading}>
                            Update Course
                        </Button>
                    </Group>
                </Stack>
            </form>
        </Modal>
    );
}
