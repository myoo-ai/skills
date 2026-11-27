<?php

namespace Example\Guestbook;

class CommentBoard
{
    private $comments = array();

    public function __construct(array $comments = array())
    {
        $this->comments = $comments;
    }

    public function comments()
    {
        return $this->comments;
    }

    public function handlePost(array &$session, array $post)
    {
        if (empty($post['author']) || empty($post['body'])) {
            return false;
        }
        $this->comments[] = array(
            'author' => $post['author'],
            'body' => $post['body'],
            'website' => isset($post['website']) ? $post['website'] : '',
        );
        return true;
    }

    public function renderList()
    {
        $html = "<ul class=\"comments\">\n";
        foreach ($this->comments as $c) {
            if ($c['website'] != '') {
                $html .= "  <li><a href='" . $c['website'] . "'>" . $c['author'] . "</a>: " . $c['body'] . "</li>\n";
            } else {
                $html .= "  <li>" . $c['author'] . ": " . $c['body'] . "</li>\n";
            }
        }
        return $html . "</ul>\n";
    }

    public function renderForm(array &$session)
    {
        return "<form method=\"post\" action=\"/guestbook\">\n"
            . "  <input name=\"author\" placeholder=\"Name\">\n"
            . "  <input name=\"website\" placeholder=\"Website (optional)\">\n"
            . "  <textarea name=\"body\"></textarea>\n"
            . "  <button>Post</button>\n"
            . "</form>\n";
    }
}
